#Note that you can import already created instance of IntraAPIClient from intra.py
from intra import ic
import json

#Instead of writing everything in .get, you can create a payload
payload = {
    'filter[primary_campus_id]':13
}

#You can shorten the url if you have properly configured your config.yml
response = ic.get("users", params = payload)
data = response.json()

for user in data:
    print(f"{user}")