import json
import os
import requests
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathvalidate import sanitize_filename


# Не забыть удалить
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Не забыть удалить
HOST = "http://tululu.org/"


def download_comments(comments_tag, filename, folder="comments/"):
    comment_selector = "span.black"

    comments = [comment.select_one(comment_selector).text
                for comment in comments_tag]

    return comments


def check_redirects(response):
    if response.status_code == 301 or response.status_code == 302:
        print("redirect")
        return True
    return False


def download_image(url, filename, folder):
    book_name = filename.text.split("::")[0].strip()

    correct_imgename = os.path.join(
        folder, "images", sanitize_filename(f"{book_name}.png"))
    response = requests.get(url, verify=False)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print("Ошибка")
        exit()

    os.makedirs(f"{folder}images", exist_ok=True)

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
        "img_scr": str(download_image),
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


def main():
    parser = create_parser()
    agrs = parser.parse_args()

    for page in range(agrs.start_page, agrs.end_page):
        print(f"Страница под номером {str(page)} качается.")

        url = "https://tululu.org/l55/"
        url_book_collection = urljoin(url, str(page))
        response_books_collection = requests.get(url_book_collection,
                                                 verify=False,
                                                 allow_redirects=False)
        if check_redirects(response_books_collection):
            continue

        soup_books_collection = BeautifulSoup(
            response_books_collection.text, "lxml")

        pages_content = soup_books_collection.select("table.d_book")
        books_links = get_content(url_book_collection, pages_content)

        for book_link in books_links:
            response_book = requests.get(book_link, verify=False)

            try:
                response_book.raise_for_status()
            except requests.exceptions.HTTPError:
                print("Ошибка")
                continue

            soup_book = BeautifulSoup(response_book.text, "lxml")
            print(book_link)
            if check_redirects(response_book) == 302:
                continue

            book_img_url = f"{HOST}"\
                f"{soup_book.select_one('.bookimage img')['src']}"
            book_text_url = soup_book.select(
                "table.d_book tr a:nth-of-type(2)")
            title_tag = soup_book.select_one("body div[id=content] h1")
            comments_tag = soup_book.select(".texts")
            book_genres = soup_book.select("span.d_book a")

            try:
                download_book_text_url = f"{HOST}{book_text_url[0]['href']}"
            except IndexError:
                print("Нет ссылки на скачивание ;(")
                continue

            comments = download_comments(comments_tag, title_tag)
            text = ["book_name", "book_author", "correct_bookname"]
            if agrs.skip_txt is False:
                text = download_txt(download_book_text_url,
                                    title_tag, agrs.dest_folder)
            none_img = "http://tululu.org//images/nopic.gif"
            book_title = str(text[0])
            book_author = str(text[1])
            book_path = str(text[2])

            if book_img_url == none_img:
                pass
            else:
                if not agrs.skip_imgs:
                    img = download_image(
                        book_img_url, title_tag, agrs.dest_folder)
            create_json(book_title, book_author, book_path, comments,
                        img, book_genres, agrs.json_path)


if __name__ == "__main__":
    main()
