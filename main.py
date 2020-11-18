import json
import os
import requests
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathvalidate import sanitize_filename

HOST = "http://tululu.org/"


def download_comments(comments_tag, filename, folder="comments/"):
    comment_selector = "span.black"

    comments = [comment.select_one(comment_selector).text
                for comment in comments_tag]

    return comments


def download_image(url, filename, folder):
    book_name = filename.text.split("::")[0].strip()

    correct_imgename = os.path.join(
        folder, "images", sanitize_filename(book_name)) + ".png"
    response = requests.get(url)

    os.makedirs(folder + "images", exist_ok=True)

    with open(os.path.join(correct_imgename), "wb") as book:
        book.write(response.content)
        return url


def get_content(page, pages_content):
    url_selector = "div.bookimage a"
    url_book = [urljoin(page, str(book.select_one(url_selector)["href"]))
                for book in pages_content]

    return url_book


def download_txt(url, filename, folder):
    book_name = filename.text.split("::")[0].strip()
    book_author = filename.text.split("::")[1].strip()

    correct_bookname = os.path.join(
        folder, "books", sanitize_filename(book_name))

    response = requests.get(url)

    os.makedirs(folder + "books", exist_ok=True)

    with open(
        os.path.join(correct_bookname) + ".txt", "w", encoding='utf-8'
    ) as book:
        book.write(response.text)
        return book_name, book_author, correct_bookname


def create_json(
    download_txt, download_comments, download_image, book_genres, folder
):
    genres = [book_genre.text for book_genre in book_genres]

    correct_bookname = os.path.join(
        folder, "json", sanitize_filename(download_txt[0]))

    book_info = {
        "title": str(download_txt[0]),
        "author": str(download_txt[1]),
        "img_scr": str(download_image),
        "comments": download_comments,
        "book_path": str(download_txt[2]),
        "genres": genres
    }

    os.makedirs(folder + "json/", exist_ok=True)

    with open(correct_bookname + ".json", "w", encoding="utf8") as mu_file:
        json.dump(book_info, mu_file, ensure_ascii=False, indent=3)


def createParser():
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


def main():
    parser = createParser()
    namespace = parser.parse_args()

    start_page = namespace.start_page
    end_page = namespace.end_page
    dest_folder = namespace.dest_folder
    json_path = namespace.json_path
    skip_imgs = namespace.skip_imgs
    skip_txt = namespace.skip_txt

    for page in range(start_page, end_page):
        print(F"Страница под номером {str(page)} качается")

        url = "http://tululu.org/l55/"
        book_page_collection = urljoin(url, str(page))
        response_books_collection = requests.get(book_page_collection)
        soup_books_collection = BeautifulSoup(
            response_books_collection.text, "lxml")

        content_selector = "table.d_book"
        pages_content = soup_books_collection.select(content_selector)
        books_links = get_content(book_page_collection, pages_content)

        for book_url in books_links:

            response_book = requests.get(book_url)
            soup_book = BeautifulSoup(response_book.text, "lxml")
            print(book_url)
            if response_book.status_code == 302:
                continue

            book_img_selector = ".bookimage img"
            title_selector = "body div[id=content] h1"
            comments_selector = ".texts"
            book_genres_seletor = "span.d_book a"
            book_download_selector = "table.d_book tr a:nth-of-type(2)"

            book_img_url = HOST + \
                str(soup_book.select_one(book_img_selector)["src"])
            book_text_url = soup_book.select(book_download_selector)
            title_tag = soup_book.select_one(title_selector)
            comments_tag = soup_book.select(comments_selector)
            book_genres = soup_book.select(book_genres_seletor)

            try:
                download_book_text_url = HOST + book_text_url[0]["href"]

            except IndexError:
                continue

            comments = download_comments(comments_tag, title_tag)
            text = ["book_name", "book_author", "correct_bookname"]
            if skip_txt is False:
                text = download_txt(download_book_text_url,
                                    title_tag, dest_folder)
            img = "http://tululu.org//images/nopic.gif"

            if book_img_url == img:
                pass
            else:
                if skip_imgs is False:
                    img = download_image(book_img_url, title_tag, dest_folder)
            create_json(text, comments, img, book_genres, json_path)


if __name__ == "__main__":
    main()
