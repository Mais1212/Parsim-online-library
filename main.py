import requests
import os

books_umber = 0

if not os.path.exists("books"):
    os.makedirs("books")

while books_umber < 8:
	books_umber += 1
	url = "http://tululu.org/txt.php?id=" + str(32160 + books_umber)
	response = requests.get(url)
	if response.url == "http://tululu.org/":
		continue
	with open('books/'+'id'+str(books_umber)+'.txt', 'w') as book:
  		book.write(response.text)