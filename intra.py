import os
import yaml
import math
import json
import time
import logging
import requests
import threading

from tqdm import tqdm
from queue import Queue
from copy import deepcopy
from pygments import highlight
from pygments.lexers.data import JsonLexer
from pygments.formatters.terminal import TerminalFormatter

requests.packages.urllib3.disable_warnings()

LOG = logging.getLogger(__name__)

class IntraAPIClient(object):
    verify_requests = False

    def __init__(self, progress_bar=False):
        base_dir = os.path.dirname(os.path.realpath(__file__))
        with open(base_dir + '/config.yml', 'r') as cfg_stream:
            config = yaml.load(cfg_stream, Loader=yaml.BaseLoader)
            self.client_id = config['intra']['client']
            self.client_secret = config['intra']['secret']
            self.token_url = config['intra']['uri']
            self.api_url = config['intra']['endpoint']
            self.scopes = config['intra']['scopes']
            self.progress_bar = progress_bar
            self.token = None

    def request_token(self):
        request_token_payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": self.scopes,
        }
        LOG.debug("Attempting to get a token from intranet")
        self.token = "token_dummy"
        res = self.request(requests.post, self.token_url, params=request_token_payload)
        rj = res.json()
        self.token = rj["access_token"]
        LOG.info(f"Got new acces token from intranet {self.token}")

    def _make_authed_header(self, header={}):
        ret = {"Authorization": f"Bearer {self.token}"}
        ret.update(header)
        return ret

    def request(self, method, url, headers={}, **kwargs):
        if not self.token:
            self.request_token()
        tries = 0
        if not url.startswith("http"):
            url = f"{self.api_url}/{url}"

        while True:
            LOG.debug(f"Attempting a request to {url}")

            res = method(
                url,
                headers=self._make_authed_header(headers),
                verify=self.verify_requests,
                **kwargs
            )

            rc = res.status_code
            if rc == 401:
                if 'www-authenticate' in res.headers:
                    _, desc = res.headers['www-authenticate'].split('error_description="')
                    desc, _ = desc.split('"')
                    if desc == "The access token expired" or desc == "The access token is invalid":
                        if self.token != "token_dummy":
                            LOG.warning(f"Server said our token {self.token} {desc.split(' ')[-1]}")
                        if tries < 5:
                            LOG.debug("Renewing token")
                            tries += 1
                            self.request_token()
                            continue
                        else:
                            LOG.error("Tried to renew token too many times, something's wrong")

            if rc == 429:
                LOG.info(f"Rate limit exceeded - Waiting {res.headers['Retry-After']}s before requesting again")
                time.sleep(float(res.headers['Retry-After']))
                continue

            if rc >= 400:
                req_data = "{}{}".format(url, "\n" + str(kwargs['params']) if 'params' in kwargs.keys() else "")
                if rc < 500:
                    raise ValueError(f"\n{res.headers}\n\nClientError. Error {str(rc)}\n{str(res.content)}\n{req_data}")
                else:
                    raise ValueError(f"\n{res.headers}\n\nServerError. Error {str(rc)}\n{str(res.content)}\n{req_data}")

            LOG.debug(f"Request to {url} returned with code {rc}")
            return res

    def get(self, url, headers={}, **kwargs):
        return self.request(requests.get, url, headers, **kwargs)

    def post(self, url, headers={}, **kwargs):
        return self.request(requests.post, url, headers, **kwargs)

    def patch(self, url, headers={}, **kwargs):
        return self.request(requests.patch, url, headers, **kwargs)

    def put(self, url, headers={}, **kwargs):
        return self.request(requests.put, url, headers, **kwargs)

    def delete(self, url, headers={}, **kwargs):
        return self.request(requests.delete, url, headers, **kwargs)

    def pages(self, url, headers={}, **kwargs):
        kwargs['params'] = kwargs.get('params', {}).copy()
        kwargs['params']['page'] = int(kwargs['params'].get('page', 1))
        kwargs['params']['per_page'] = kwargs['params'].get('per_page', 100)
        data = self.get(url=url, headers=headers, **kwargs)
        total = data.json()
        if 'X-Total' not in data.headers:
            return total
        last_page = math.ceil(int(data.headers['X-Total']) /
            int(data.headers['X-Per-Page']))
        for page in tqdm(range(kwargs['params']['page'], last_page),
            initial=1, total=last_page - kwargs['params']['page'] + 1,
            desc=url, unit='p', disable=not self.progress_bar):
            kwargs['params']['page'] = page + 1
            total += self.get(url=url, headers=headers, **kwargs).json()
        return total


    def pages_threaded(self, url, headers={}, threads=20, stop_page=None,
                                                            thread_timeout=15, **kwargs):
        def _page_thread(url, headers, queue, **kwargs):
            queue.put(self.get(url=url, headers=headers, **kwargs).json())

        kwargs['params'] = kwargs.get('params', {}).copy()
        kwargs['params']['page'] = int(kwargs['params'].get('page', 1))
        kwargs['params']['per_page'] = kwargs['params'].get('per_page', 100)

        data = self.get(url=url, headers=headers, **kwargs)
        total = data.json()

        if 'X-Total' not in data.headers:
            return total

        last_page = math.ceil(
            float(data.headers['X-Total']) / float(data.headers['X-Per-Page'])
        )
        last_page = stop_page if stop_page and stop_page < last_page else last_page
        page = kwargs['params']['page'] + 1
        pbar = tqdm(initial=1, total=last_page - page + 2,
            desc=url, unit='p', disable=not self.progress_bar)

        while page <= last_page:
            active_threads = []
            for _ in range(threads):
                if page > last_page:
                    break
                queue = Queue()
                kwargs['params']['page'] = page
                at = threading.Thread(target=_page_thread,
                    args=(url, headers, queue), kwargs=deepcopy(kwargs))

                at.start()
                active_threads.append({
                    'thread': at,
                    'page': page,
                    'queue': queue
                    })
                page += 1

            for th in range(len(active_threads)):
                active_threads[th]['thread'].join(timeout=threads * thread_timeout)
                if active_threads[th]['thread'].is_alive():
                    raise RuntimeError(f'Thread timeout after waiting for {threads * thread_timeout} seconds')
                total += active_threads[th]['queue'].get()
                pbar.update(1)

        pbar.close()
        return total

    def progress_disable(self):
        self.progress_bar = False

    def progress_enable(self):
        self.progress_bar = True

    def prompt(self):
        while 42:
            qr = input("$> http://api.intra.42.fr/v2/")

            if qr == "token":
                print(ic.token)
                continue

            try:
                ret = ic.get(qr)
                json_str = json.dumps(ret.json(), indent=4)
                print(highlight(json_str, JsonLexer(), TerminalFormatter()))
            except Exception as e:
                print(e)

ic = IntraAPIClient()
