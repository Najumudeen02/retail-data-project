import requests
import csv

url = "https://jsonplaceholder.typicode.com/posts"
#url = "https://this-domain-does-not-exist-12345.com"

all_posts =[]
page = 1

#day 5 - Added function to call the api multiple times
def fetch_posts(page, limit):
    param = {
         "_page": page,
         "_limit": limit
             }
    try:
        response = requests.get(url,params=param)
        if response.status_code == 200:
            return response.json()
        else: 
            print("Status Code:", response.status_code())
            return all_posts

    except Exception as conn_error:
        print("Connection went wrong", conn_error)
        return all_posts

try:
    while True:
        #Day 5 code with function logic
        data = fetch_posts(page,10)

        if not data:
            break
        all_posts.extend(data)
        page += 1

    #Day 6 - Code to get specific data from all posts - start
    clean_posts = []
    for post in all_posts:

        clean_post = {
            "user_id": post["userId"],
            "post_id": post["id"],
            "title": post["title"]
        }
        clean_posts.append(clean_post)

    if clean_posts:
        print("Number of clean posts:", len(clean_posts))
        print(clean_posts[0])
        print(clean_posts[-1])    

    #day 6 - CSV file creation and writing
    with open("clean_posts.csv","w",newline="",encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, 
            fieldnames=["user_id" , "post_id", "title"])
        writer.writeheader()
        writer.writerows(clean_posts)

    #day 6 - File reading logic
    with open("clean_posts.csv", "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        csv_posts = list(reader)

    for post in csv_posts:
        post["user_id"] = int(post["user_id"])
        post["post_id"] = int(post["post_id"])
        
    print(type(csv_posts[0]["user_id"]))
    print(type(csv_posts[0]["post_id"]))
    print(type(csv_posts[0]["title"]))
    print("CSV records:", len(csv_posts))
    print("First record:", csv_posts[0])
    print("Last record:", csv_posts[-1])

    #day 6 - get post ids to verify number of unique ids
    post_ids = []
    for post in clean_posts:
        post_ids.append(post["post_id"])
    
    total_ids = len(post_ids)
    unique_ids = len(set(post_ids))

    if total_ids == unique_ids:
        print("There are no duplicates in the clean posts")
    else:
        print("Duplicates exists in clean posts")

    #day 6 - To see if the clean posts has any missing values
       
    missing_titles = 0
    for post in clean_posts:
        if not post["title"]:
            missing_titles += 1

    if missing_titles == 0:    
        print("No missing titles found")
    else:
        print("WARNING: X posts have missing titles")

    print("Total IDs:", len(post_ids))
    print("Unique IDs:", len(set(post_ids)))
    # Day 6 - Changes ends here

    #Day 5 Changes to get data after error in function
    print("Total posts:", len(all_posts))
    if all_posts:
        print("First post ID:", all_posts[0]["id"])
        print("Last post ID:", all_posts[-1]["id"])
    else:
        print("No posts were retrieved.")
    #Day 5 changes ends here


        #response = requests.get(url,params=param)
        #print("Page:", param["_page"])
        #data = response.json()

     

        # print("Number of records:",len(data))
        # print("First post ID:",data[0]['id'])
        # print("Last post ID:",data[-1]['id'])
        


    # if response.status_code == 200:
    #   data = response.json()
    #   print(type(data))
    #   print(len(data))
    # elif response.status_code == 404:
    #   print("Post Not Found")
    # else:
    #   print("Request failed.")
    #   print("Status Code",response.status_code)
    

   

except Exception as e:
    print("Something went wrong", e)


# print(len(data))
# print(data[0]["id"])
# print(data[-1]["id"])
# # user_counts = {}
# # count=0
# # for post in data:
# #     user_id = post['userId']
    
# #     if user_id in user_counts:
# #         count += 1
# #         user_counts[user_id]= count
      
# #     else:
# #         count = 1
# #         user_counts[user_id] = count
      
# # print(user_counts)