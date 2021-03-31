import argparse
import json
import os
import requests
import urllib3

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
HOST = "http://tululu.org/"


def download_comments(comments_tag, filename, folder="comments/"):
    comment_selector = "span.black"

    comments = [comment.select_one(comment_selector).text
                for comment in comments_tag]

    return comments


def has_redirects(response):
    if response.status_code == 301 or response.status_code == 302:
        print("redirect")
        return True
    elif not response.ok:
        print("Ссылка не рабочая")
        return True


def download_image(url, filename, folder):
    book_name = filename.text.split("::")[0].strip()

    correct_imgename = os.path.join(
        folder, "images", sanitize_filename(f"{book_name}.png"))
    response = requests.get(url, verify=False)
    raise requests.exceptions.HTTPError

    os.makedirs(f"{folder}images", exist_ok=True)

    with open(os.path.join(correct_imgename), "wb") as book:
        book.write(response.content)
        return url


def get_books_links(pages, pages_content):
    url_selector = "div.bookimage a"
    url_book = [urljoin(pages, str(book.select_one(url_selector)["href"]))
                for book in pages_content]

    return url_book


def download_txt(url, filename, folder):
    book_name = filename.text.split("::")[0].strip()
    book_author = filename.text.split("::")[1].strip()

    correct_bookname = os.path.join(
        folder, "books", sanitize_filename(f"{book_name}.txt"))

    response = requests.get(url, verify=False)
    response.raise_for_status()

    os.makedirs(f"{folder}books", exist_ok=True)

    with open(
        os.path.join(correct_bookname), "w", encoding='utf-8'
    ) as book:
        book.write(response.text)
        return book_name, book_author, correct_bookname


def create_json(
        book_title, book_author, book_path, download_comments, download_image,
        book_genres, folder):
    genres = [book_genre.text for book_genre in book_genres]

    correct_bookname = os.path.join(
        folder, "json", sanitize_filename(book_title))

    book_info = {
        "title": book_title,
        "author": book_author,
        "img_url": str(download_image),
        "comments": download_comments,
        "book_path": book_path,
        "genres": genres
    }

    os.makedirs(f"{folder}json/", exist_ok=True)

    with open(f"{correct_bookname}.json", "w", encoding="utf8") as mu_file:
        json.dump(book_info, mu_file, ensure_ascii=False, indent=3)


def create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-sp",
        "--start_page",
        type=int,
        help="Какой страницой начать?",
        default=1
    )

    parser.add_argument(
        "-ep",
        "--end_page",
        type=int,
        help="Какой страницой закончить?",
        default=701
    )

    parser.add_argument(
        "-df",
        "--dest_folder",
        type=str,
        help="Путь к каталогу с результатами парсинга:\
         картинкам, книгам, JSON.",
        default="library/"
    )

    parser.add_argument(
        "-skip_i",
        "--skip_imgs",
        help="Не скачивать картинки",
        action='store_true'
    )

    parser.add_argument(
        "-skip_t",
        "--skip_txt",
        help="Не скачивать книги",
        action='store_true'
    )

    parser.add_argument(
        "-jp",
        "--json_path",
        type=str,
        help="Указать свой путь к *.json файлу с результатами",
        default="library/")

    return parser


def create_links_collection(page, args):
    url = "https://tululu.org/l55/"
    url_book_collection = urljoin(url, str(page))
    response_books_collection = requests.get(url_book_collection,
                                             verify=False,
                                             allow_redirects=False)
    if has_redirects(response_books_collection):
        return

    soup_books_collection = BeautifulSoup(
        response_books_collection.text, "lxml")

    pages_content = soup_books_collection.select("table.d_book")
    links_collection = get_books_links(url_book_collection, pages_content)
    return links_collection


def make_library(args, book_img_url, book_text_url, title_tag, comments_tag,
                 book_genres):

    download_book_text_url = f"{HOST}{book_text_url['href']}"

    downloaded_comments = download_comments(comments_tag, title_tag)
    text = ["book_name", "book_author", "correct_bookname"]
    if not args.skip_txt:
        text = download_txt(download_book_text_url,
                            title_tag, args.dest_folder)
    none_img = "http://tululu.org//images/nopic.gif"
    book_title = str(text[0])
    book_author = str(text[1])
    book_path = str(text[2])

    if book_img_url == none_img:
        img = none_img
        pass
    elif not args.skip_imgs:
        img = download_image(
            book_img_url, title_tag, args.dest_folder)

    create_json(book_title, book_author, book_path, downloaded_comments,
                img, book_genres, args.json_path)


def get_book_content(book_link, args):
    if book_link is None:
        print("Ошибка")
        return

    response_book = requests.get(book_link, verify=False)

    if not response_book.ok:
        print("Ошибка")
        return

    soup_book = BeautifulSoup(response_book.text, "lxml")
    if has_redirects(response_book):
        return

    book_img_url = f"{HOST}"\
        f"{soup_book.select_one('.bookimage img')['src']}"
    book_text_url = soup_book.select_one(
        "table.d_book tr a:nth-of-type(2)")
    title_tag = soup_book.select_one("body div[id=content] h1")
    comment_tags = soup_book.select(".texts")
    book_genres = soup_book.select("span.d_book a")

    make_library(args, book_img_url, book_text_url, title_tag, comment_tags,
                 book_genres)


def main():
    parser = create_parser()
    args = parser.parse_args()

    for page in range(args.start_page, args.end_page):
        print(f"Страница под номером {page} качается.")
        links_collection = create_links_collection(page, args)

        for book_link in links_collection:
            try:
                get_book_content(book_link, args)
            except TypeError:
                print("Нет ссылки на скачивание ;(")
                pass
            except requests.exceptions.HTTPError:
                print("Ошибка")
                exit()


if __name__ == "__main__":
    main()
