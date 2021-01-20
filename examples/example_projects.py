from intra import ic
#As noted in the example3, here we imported the whole config
import config

#Example of using filtering and sorting
#We filter by Hive Helsinki campus_id and main cursus_id
#Then we sort in descending order (-final mark)
payload = {
    'filter[primary_campus]':config.campus_id,
    'filter[cursus]':config.cursus_id,
    'sort':"-final_mark"
}

#Here we use .pages_threaded to pull all libft teams, it is the same as .pages but with multithreading
data = ic.pages_threaded("projects/1/teams", params=payload)

#Print some (interesting?) data
for item in data:
    print(f"Final mark: {item['final_mark']} Login: ", end ="")
    print(item['users'][0]['id'])