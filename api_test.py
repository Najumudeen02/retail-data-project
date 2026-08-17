import requests


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

    print("Total posts:", len(all_posts))
    if all_posts:
        print("First post ID:", all_posts[0]["id"])
        print("Last post ID:", all_posts[-1]["id"])
    else:
        print("No posts were retrieved.")
    


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