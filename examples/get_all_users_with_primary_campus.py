# Import the IntraAPIClient class from intra
from intra import ic
from config import campus_id

payload = {
    "filter[primary_campus_id]":campus_id
}

# Let's see the progress
ic.progress_bar=True

# GET all users with specified primary campus
# Note that .pages_threaded returns json
data = ic.pages_threaded("users", params=payload)

for user in data:
    print(user)
