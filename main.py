import json
import os
import requests
import lxml
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathvalidate import sanitize_filename

PAGE_NUMBER = 0
HOST ="http://tululu.org/"

def download_comments(comments_tag, filename, folder = 'comments/'):
	book_name = filename.text.split("::")[0].strip()
	correct_commentname = "(Коментарии)"+sanitize_filename(folder + book_name)
	comments_list = []
	for comment in comments_tag:
		comments_list.append(comment.find("span", class_ = "black").text)

	comments_str = ' '.join(comments_list)

	return comments_list

def download_image(url, filename, folder = 'images/'):
	book_name = filename.text.split("::")[0].strip()

	correct_imgename = folder + sanitize_filename(book_name)
	response = requests.get(url)
	
	if not os.path.exists(folder):
		os.makedirs(folder)

	with open(os.path.join(correct_imgename) + '.png', 'wb') as book:
  		book.write(response.content)
  		return url

def get_content(page, pages_content):
	url_book = []
	for book in pages_content :
		url_book.append(urljoin(page, book.find("a").get("href")))
	return url_book

def download_txt(url, filename, folder = 'books/'):
	book_name = filename.text.split("::")[0].strip()
	book_author = filename.text.split("::")[1].strip()
	correct_bookname = folder + sanitize_filename(book_name)
	
	response = requests.get(url)
	
	if not os.path.exists(folder):
		os.makedirs(folder)

	with open(os.path.join(correct_bookname) + '.txt', 'w') as book:
  		book.write(response.text)
  		return book_name, book_author, correct_bookname

def create_json(download_txt,download_comments, download_image, book_genres, folder = 'json/'):
	genres = []
	for book_genre in book_genres:
		genres.append(book_genre.text)

	book_info = {
		"title" : str(download_txt[0]),
		"author" : str(download_txt[1]),
		"img_scr" : str(download_image),
		"comments" : download_comments,
		"book_path" : str(download_txt[2]),
		"genres" : genres
	}
	if not os.path.exists(folder):
		os.makedirs(folder)
	print(type(download_comments))

	with open(folder + download_txt[0]+".json", "w", encoding='utf8') as my_file:
  		json.dump(book_info, my_file, ensure_ascii=False, indent=3)


while PAGE_NUMBER < 2:
	PAGE_NUMBER += 1


	url = 'http://tululu.org/l55/'
	response_books_collection = requests.get(url)
	soup_books_collection = BeautifulSoup(response_books_collection.text, 'lxml')
	pages_content = soup_books_collection.find("div", id = "content").find_all("table")
	book_page_collection = urljoin(url, str(PAGE_NUMBER))
	books_links = get_content(book_page_collection, pages_content)
	print(book_page_collection)


	for book_url in books_links:
		response_book = requests.get(book_url, allow_redirects = False)
		soup_book = BeautifulSoup(response_book.text, 'lxml')

		if response_book.status_code == 302:
			continue

		book_img_url = HOST + soup_book.find("div", class_ = "bookimage").find("img").get("src")
		title_tag = soup_book.find("div", id = "content").find('h1')
		comments_tag = soup_book.find_all("div", class_ = "texts")
		book_genres = soup_book.find("span", class_ = "d_book").find_all("a")

		comments = download_comments(comments_tag, title_tag)
		text =  download_txt(book_url,title_tag)
		if book_img_url == "http://tululu.org//images/nopic.gif":
			pass
		else :
			img = download_image(book_img_url,title_tag)
		create_json(text, comments, img, book_genres)