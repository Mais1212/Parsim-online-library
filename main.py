from bs4 import BeautifulSoup
import requests
import lxml
import os
from pathvalidate import sanitize_filename

def download_txt(url, filename, folder = 'books/'):
	correct_filename = sanitize_filename(filename)
	response = requests.get(url)
	
	if not os.path.exists(folder):
		os.makedirs(folder)

	with open(os.path.join(folder + correct_filename) + '.txt', 'w') as book:
  		book.write(response.text)

books_umber = 0

while books_umber < 10:
	books_umber += 1
	url = 'http://tululu.org/b' + str(books_umber)
	book_url = 'http://tululu.org/txt.php?id=' + str(books_umber)
	response = requests.get(url)
	response_book = requests.get(book_url)
	print(response_book.url)
	if response_book.url == "http://tululu.org/":
		print("Error")
		continue
	soup = BeautifulSoup(response.text, 'lxml')
	title_tag = soup.find("div", id="content").find('h1')
	download_txt(book_url,title_tag.text.split("::")[0].strip())