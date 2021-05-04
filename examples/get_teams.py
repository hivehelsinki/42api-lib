from intra import ic

# Simple GET for all teams, without pagination, GET will only return first 30 results
response = ic.get("teams")
if response.status_code == 200: # Is status OK?
    data = response.json()

for team in data:
    print(team)