from intra import ic
import config

# Filter by primary campus and cursus and sort by final mark in descending order
payload = {
    'filter[primary_campus]':config.campus_id,
    'filter[cursus]':config.cursus_id,
    'sort':"-final_mark"
}

# Let's see the progress
ic.progress_bar=True

# pages_threaded pulls all the specified data
# Note that .pages_threaded returns json
data = ic.pages_threaded("projects/1/teams", params=payload)

# Print some (interesting?) data
for team in data:
    print(f"Final mark: {team['final_mark']} Login: {team['users'][0]['id']}")
