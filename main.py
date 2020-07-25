from bs4 import BeautifulSoup
import requests
import lxml
import os
from pathvalidate import sanitize_filename

BOOKS_NUMBER = 0
HOST ="http://tululu.org/"

def download_comments(comments, filename, folder = 'books/'):
	correct_filename = "(Коментарии)"+sanitize_filename(filename) 
	
	if not os.path.exists(folder):
		os.makedirs(folder)

	with open(os.path.join(folder +correct_filename) + '.txt', 'w') as book:
  		book.write(comments.text)

def download_image(url, filename, folder = 'images/'):
	correct_filename = sanitize_filename(filename)
	response = requests.get(url)
	
	if not os.path.exists(folder):
		os.makedirs(folder)

	with open(os.path.join(folder + correct_filename) + '.png', 'wb') as book:
  		book.write(response.content)


def download_txt(url, filename, folder = 'books/'):
	correct_filename = sanitize_filename(filename)
	response = requests.get(url)
	
	if not os.path.exists(folder):
		os.makedirs(folder)

	with open(os.path.join(folder + correct_filename) + '.txt', 'w') as book:
  		book.write(response.text)


while BOOKS_NUMBER < 11:
	BOOKS_NUMBER += 1
	url = 'http://tululu.org/b' + str(BOOKS_NUMBER)
	book_url = 'http://tululu.org/txt.php?id=' + str(BOOKS_NUMBER)
	response = requests.get(url)
	book_response = requests.get(book_url, allow_redirects=False)

	if book_response.status_code == 302:
		continue

	soup = BeautifulSoup(response.text, 'lxml')
	book_img_url = HOST + soup.find("div", class_ = "bookimage").find("img").get("src")
	title_tag = soup.find("div", id = "content").find('h1')
	comments_tag = soup.find_all("div", class_ = "texts")
	book_genre = soup.find("span", class_ = "d_book").find_all("a")
	for genre in book_genre :
		print(genre.text)

	if comments_tag :
		for comment in comments_tag:
			comments = comment.find("span", class_ = "black")
			download_comments(comments, title_tag.text.split("::")[0].strip())

	download_txt(book_url,title_tag.text.split("::")[0].strip())
	download_image(book_img_url,str(BOOKS_NUMBER))