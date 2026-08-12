import requests

url = "https://this-domain-does-not-exist-12345.com"


try:
    response = requests.get(url)
    #print("Status code:",response.status_code)
    if response.status_code == 200:
      data = response.json()
      print(data)
    elif response.status_code == 404:
      print("Post Not Found")
    else:
      print("Request failed.")
      print("Status Code",response.status_code)

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

