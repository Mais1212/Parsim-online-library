# Парсер книг с сайта tululu.org

Парсер раздела книг научной фантастики с онлайн [Библиотеки](http://tululu.org)

### Как установить

Для запуска нужен Python 3.8.4 и библекотки для него

Библиотки:

	requests==2.24.0
	lxml==4.5.2
	beautifulsoup4==4.9.1
	urljoin==1.0.0
	pathvalidate==2.3.0

### Аргументы

Для удобства пользователя в коде есть аргументы, их нужно указывать после ' python main.py '

Аргументы :

		"-sp", "--start_page" - Какой страницой начать
		
		"-ep", "--end_page" - Какой страницой закончить
		
		"-df", "--dest_folder" - Путь к каталогу с результатами парсинга: картинкам, книгам, JSON.
		
		"-skip_i", "--skip_imgs" - Если указано, скрипт не будет скачивать картинки
		
		"-skip_t", "--skip_txt" - Если указано, то скрипт не будет скачивать книги
		
		"-jp", "--json_path" - Указать свой путь к *.json файлу с результатами

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).