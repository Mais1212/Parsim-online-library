import json
import os
import requests
import lxml
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathvalidate import sanitize_filename
import argparse

HOST ="http://tululu.org/"

def download_comments(comments_tag, filename, folder = "comments/"):
	book_name = filename.text.split("::")[0].strip()
	selector_comment = "span.black"

	correct_commentname = "(Коментарии)"+sanitize_filename(folder + book_name)
	comments_list = []
	for comment in comments_tag:
		comments_list.append(comment.select_one(selector_comment).text)

	comments_str = " ".join(comments_list)

	return comments_list

def download_image(url, filename, folder):
	book_name = filename.text.split("::")[0].strip()

	correct_imgename = os.path.join( folder + "images/" + sanitize_filename(book_name))
	response = requests.get(url)
	
	if not os.path.exists(folder + "images/"):
		os.makedirs(folder + "images/")

	with open(os.path.join(correct_imgename) + ".png", "wb") as book:
  		book.write(response.content)
  		return url

def get_content(page, pages_content):
	url_book = []
	selector_url = "div.bookimage a"
	for book in pages_content :
		url_book.append(urljoin(page, str(book.select_one(selector_url)["href"])))
	return url_book

def download_txt(url, filename, folder):
	book_name = filename.text.split("::")[0].strip()
	book_author = filename.text.split("::")[1].strip()

	correct_bookname = os.path.join( folder + "books/" + sanitize_filename(book_name))
	
	response = requests.get(url)
		
	if not os.path.exists(folder + "books/"):
		os.makedirs(folder + "books/")

	with open(os.path.join(correct_bookname) + ".txt", "w", encoding='utf-8') as book:
  		book.write(response.text)
  		return book_name, book_author, correct_bookname

def create_json(download_txt,download_comments, download_image, book_genres, folder):
	genres = []
	correct_bookname = os.path.join( folder + "json/" + sanitize_filename(download_txt[0]))

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

	if not os.path.exists(folder + "json/"):
		os.makedirs(folder + "json/")

	with open(correct_bookname + ".json", "w", encoding="utf8") as mu_file:
  		json.dump(book_info, mu_file, ensure_ascii=False, indent=3)

def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-sp", "--start_page", type= int,
     help = "Какой страницой начать", default = 1)

    parser.add_argument("-ep", "--end_page", type = int,
     help = "Какой страницой закончить", default = 701)

    parser.add_argument("-df", "--dest_folder",type = str,
     help = "Путь к каталогу с результатами парсинга: картинкам, книгам, JSON.", default = "library/")
    
    parser.add_argument("-skip_i", "--skip_imgs", help = "Не скачивать картинки", action='store_true')

    parser.add_argument("-skip_t", "--skip_txt", help = "Не скачивать книги", action='store_true')

    parser.add_argument("-jp", "--json_path", type = str,
     help = "Указать свой путь к *.json файлу с результатами", default = "library/")
 
    return parser


parser = createParser()
namespace = parser.parse_args()


start_page = namespace.start_page
end_page = namespace.end_page
dest_folder = namespace.dest_folder
json_path = namespace.json_path
skip_imgs = namespace.skip_imgs
skip_txt = namespace.skip_txt


while start_page < end_page:
	print("Страница под номером " + str(start_page) + " качается")

	url = "http://tululu.org/l55/"
	book_page_collection = urljoin(url, str(start_page))
	response_books_collection = requests.get(book_page_collection)
	soup_books_collection = BeautifulSoup(response_books_collection.text, "lxml")


	selector_content = "table.d_book"
	pages_content = soup_books_collection.select(selector_content)
	books_links = get_content(book_page_collection, pages_content)


	for book_url in books_links:
		
		response_book = requests.get(book_url, allow_redirects = False)
		soup_book = BeautifulSoup(response_book.text, "lxml")

		if response_book.status_code == 302:
			continue

		selector_book_img = ".bookimage img"
		selector_title = "body div[id=content] h1"
		selector_comments = ".texts"
		seletor_book_genres = "span.d_book a"
		selector_book_download = "table.d_book tr a:nth-of-type(2)"
		book_img_url = HOST + str(soup_book.select_one(selector_book_img)["src"])
		book_text_url = soup_book.select(selector_book_download)
		title_tag = soup_book.select_one(selector_title)
		comments_tag = soup_book.select(selector_comments)
		book_genres = soup_book.select(seletor_book_genres)

		try:
			download_book_text_url = HOST + book_text_url[0]["href"]
		
		except IndexError:
			continue

		

		comments = download_comments(comments_tag, title_tag)
		text = ["book_name", "book_author", "correct_bookname"]
		if skip_txt == False:
			text =  download_txt(download_book_text_url,title_tag, dest_folder)
		img = "http://tululu.org//images/nopic.gif"

		if book_img_url == img:
			pass
		else :
			if skip_imgs == False:
				img = download_image(book_img_url,title_tag, dest_folder)
		create_json(text, comments, img, book_genres, json_path)
	start_page += 1