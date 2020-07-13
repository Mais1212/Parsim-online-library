import requests
import os

if not os.path.exists("books"):
    os.makedirs("books")

for id in range(1,10):
	url = "http://tululu.org/txt.php?id=" + str(32160 + id)
	print(url)
	response = requests.get(url)
	response.raise_for_status()
	with open('books/'+'id'+str(id)+'.txt', 'w') as book:
  		book.write(response.text)