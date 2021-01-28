# Import the IntraAPIClient class from intra
from intra import IntraAPIClient
from config import campus_id
import json

# Create instance of IntraAPIClient
client = IntraAPIClient()

# .get request, convert to json
# Note that this gets us only first 30 users, since the resource is paginated
# Make sure to check the status code to know if the .get was successful
response = client.get(f"https://api.intra.42.fr/v2/users?filter[primary_campus_id]={campus_id}")
if response.status_code == 200:
    data = response.json()

# Print it!
for user in data:
    print(f"{user}")