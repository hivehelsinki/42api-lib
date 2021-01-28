from intra import ic
# Import data from config.py
# Could also: "import config" and then use: "config.campus_id"
from config import campus_id
import json

# You can also use f-string and if you have config.py file, you can define values there
# Make sure to check the status code to know if the .get was successful
response = ic.get(f"campus_users?filter[campus_id]={campus_id}")
if response.status_code == 200:
    data = response.json()

for user in data:
    print(f"{user}")