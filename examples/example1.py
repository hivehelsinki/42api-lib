#Import the IntraAPIClient class from intra
from intra import IntraAPIClient
import json

#Create instance of IntraAPIClient
client = IntraAPIClient()

#.get request, convert to json
#Note that this gets us only first 30 users, since the resource is paginated
response = client.get("https://api.intra.42.fr/v2/users?filter[primary_campus_id]=13")
data = response.json()

#Print it!
for user in data:
    print(f"{user}")