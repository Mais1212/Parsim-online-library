import requests

url = "http://tululu.org/txt.php?id=32168"
response = requests.get(url)
response.raise_for_status()
book = open('book.txt', 'w')
book.write(response.text)
book.close()