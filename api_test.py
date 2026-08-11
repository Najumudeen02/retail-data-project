import requests

response = requests.get("https://jsonplaceholder.typicode.com/posts")

data = response.json()

user_counts = {}
count=0
for post in data:
    user_id = post['userId']
    
    if user_id in user_counts:
        count += 1
        user_counts[user_id]= count
      
    else:
        count = 1
        user_counts[user_id] = count
      

print(user_counts)

