import requests

url = "https://jsonplaceholder.typicode.com/posts"

all_posts =[]
page = 1


try:
    while True:
        
        param = {
             "_page": page,
            "_limit": 10
                }
        page += 1
        response = requests.get(url,params=param)
        #print("Page:", param["_page"])

        data = response.json()
        if not data:
            break
        
        # print("Number of records:",len(data))
        # print("First post ID:",data[0]['id'])
        # print("Last post ID:",data[-1]['id'])
        
        all_posts.extend(data)

    # if response.status_code == 200:
    #   data = response.json()
    #   print(type(data))
    #   print(len(data))
    # elif response.status_code == 404:
    #   print("Post Not Found")
    # else:
    #   print("Request failed.")
    #   print("Status Code",response.status_code)
    
    print("Total posts:", len(all_posts))
    print("First post ID:", all_posts[0]["id"])
    print("Last post ID:", all_posts[-1]["id"])
   

except Exception as e:
    print("Something went wrong", e)


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

