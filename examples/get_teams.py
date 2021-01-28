# Note that you can import already created instance of IntraAPIClient from intra.py
from intra import ic
from config import campus_id

import json


# Instead of writing everything in .get, you can create a payload
payload = {
    'filter[primary_campus]':campus_id
}

# You can also send the complere URL, eg. https://api.intra.42.fr/v2/teams
# Make sure to check the status code to know if the .get was successful
response = ic.get("teams", params = payload)
if response.status_code == 200:
    data = response.json()

for user in data:
    print(f"{user}")