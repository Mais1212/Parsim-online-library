import argparse
import datetime
import json
import os
import requests
import urllib3

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin

HOST = "http://tululu.org/"


class RedirectError(TypeError):
    pass


class BookTxtExistenceError(TypeError):
    pass


def raise_for_redirect(response):
    if response.status_code == 301 or response.status_code == 302:
        raise RedirectError


def download_image(url, book_name, folder):
    img_path = os.path.join(
        folder, "images", sanitize_filename(f"{book_name}.png"))

    response = requests.get(url, verify=False)

    os.makedirs(os.path.join(folder, "images"), exist_ok=True)

    with open(img_path, "wb") as book:
        book.write(response.content)
        return img_path


def get_books_links(page_url, page_content):
    url_selector = "div.bookimage a"
    books_url = [urljoin(page_url, book.select_one(url_selector)["href"])
                 for book in page_content]
    return books_url


def download_txt(url, title_tag, folder):
    book_title = title_tag.text.split("::")[0].strip()
    book_name = f"{book_title}"

    book_author = title_tag.text.split("::")[1].strip()

    book_path = os.path.join(
        folder, "books", sanitize_filename(f"{book_name}.txt"))

    response = requests.get(url, verify=False)
    response.raise_for_status()
    raise_for_redirect(response)

    os.makedirs(os.path.join(folder, "books"), exist_ok=True)

    with open(book_path, "w", encoding='utf-8') as book:
        book.write(response.text)
        return book_path, book_author, book_name


def create_json(
        book_name, book_author, book_path, comments,
        img_path, book_genres, folder, timestamp):

    json_path = os.path.join(
        folder, "json", sanitize_filename(f'{book_name}.json'))

    book = {
        "title": book_name,
        "author": book_author,
        "img_path": img_path,
        "comments": comments,
        "book_path": book_path,
        "genres": book_genres,
        "timestamp": timestamp,
    }

    os.makedirs(os.path.join(folder, "json"), exist_ok=True)

    with open(json_path, "w", encoding="utf8") as file:
        json.dump(book, file, ensure_ascii=False, indent=3)


def create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-ps",
        "--page_start",
        type=int,
        help="Какой страницой начать?",
        default=1
    )

    parser.add_argument(
        "-pe",
        "--page_end",
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
        default="library"
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
        default="library")

    return parser


def collect_links(page_number, args):
    url = "https://tululu.org/l55/"
    page_url = urljoin(url, str(page_number))
    response_books_collection = requests.get(page_url,
                                             verify=False,
                                             allow_redirects=False)
    response_books_collection.raise_for_status()
    raise_for_redirect(response_books_collection)
    soup_books_collection = BeautifulSoup(
        response_books_collection.text, "lxml")

    page_content = soup_books_collection.select("table.d_book")
    links = get_books_links(page_url, page_content)
    return links


def make_library(args, book_img_url, book_text_url, title_tag, comment_tags,
                 book_genres_tag):

    book_text_url = f"{HOST}{book_text_url['href']}"

    if not args.skip_txt:
        book_path, book_author, book_name = download_txt(
            book_text_url,
            title_tag,
            args.dest_folder)

    default_img = "http://tululu.org//images/nopic.gif"

    if book_img_url == default_img:
        img_path = None
        pass
    elif not args.skip_imgs:
        img_path = download_image(
            book_img_url,
            book_name,
            args.dest_folder)

    book_genres = [book_genre.text for book_genre in book_genres_tag]
    comments = [comment.text for comment in comment_tags]
    timestamp = datetime.datetime.now().timestamp()
    create_json(book_name, book_author, book_path, comments,
                img_path, book_genres, args.json_path, timestamp)


def download_book_content(book_link, args):
    if book_link is None:
        raise requests.exceptions.HTTPError

    response_book = requests.get(book_link, verify=False)

    response_book.raise_for_status()
    raise_for_redirect(response_book)

    soup_book = BeautifulSoup(response_book.text, "lxml")

    book_img_url = f"{HOST}{soup_book.select_one('.bookimage img')['src']}"
    book_text_url = soup_book.select_one("table.d_book tr a:nth-of-type(2)")
    title_tag = soup_book.select_one("body div[id=content] h1")
    comment_tags = soup_book.select(".texts span.black")
    book_genres = soup_book.select("span.d_book a")

    if book_text_url:
        make_library(args, book_img_url, book_text_url, title_tag,
                     comment_tags, book_genres)
    else:
        raise BookTxtExistenceError


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    parser = create_parser()
    args = parser.parse_args()

    for page_number in range(args.page_start, args.page_end):
        print(f"Страница под номером {page_number} качается.")
        try:
            links = collect_links(page_number, args)
        except RedirectError:
            continue

        for book_link in links:
            try:
                download_book_content(book_link, args)
            except BookTxtExistenceError:
                print("Нет ссылки на скачивание ;(")
                continue
            except requests.exceptions.HTTPError:
                print("Ошибка")
                exit()
            except RedirectError:
                print("Redirect")
                continue


if __name__ == "__main__":
    main()
