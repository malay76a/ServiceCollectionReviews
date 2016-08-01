import configparser
import logging
import sqlite3
from urllib.parse import unquote
from wsgiref.simple_server import make_server

import firstruncheck

# В данном блоке загружается информация из конфигурациооного файла
try:
    # подключаемся к файлу с логами
    logging.basicConfig(
        filename='app.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    conf = configparser.RawConfigParser()
    conf.read("app.cfg")
    HOST = conf.get("server", "host")
    PORT = int(conf.get("server", "port"))
    DB_NAME = conf.get("database", "db_name") + ".db"
except Exception:
    logging.warning('Ошибка при подключении к файлу конфигурации')
    quit()


def raw_query_string_to_dict(param):
    """
    Функция для перевода сырой строки в соварь параметров
    :param param: сырая строка параметров полученных в запросе
    :return: возвращает словарь параметров типа ключ - значение

    """
    param = unquote(param)
    list_param = param.split("&")
    dict_param = {item[:item.find("=")]: item[item.find("=")+1:] for item in list_param}
    return dict_param


def check_db_users_email_phone(param):
    """
    Проверка по емайлу или новеру телефона наличие пользователя в базе данных
    для идентификации пользователя по некоторым уникальным значениям
    :return: 0 если пользователь не найден, либо число = id найденному пользователю
    """
    checkuser = "SELECT * FROM users WHERE"
    if param['TELEPHON'] != "":
        checkuser += " TELEPHON='" + param['TELEPHON'] + "'"
    if param['EMAIL'] != "":
        if param['TELEPHON'] != "":
            checkuser += "OR EMAIL='" + param['EMAIL'] + "'"
        else:
            checkuser += " EMAIL='" + param['EMAIL'] + "'"
    checkuser += " AND FIRST_NAME='" + param['FIRST_NAME'] + "' AND LAST_NAME='" + param['LAST_NAME'] + "'"
    try:
        db = sqlite3.connect(DB_NAME)
        cursor = db.cursor()
        user = cursor.execute(checkuser).fetchall()
        db.close()
    except sqlite3.Error:
        logging.warning("check_db_users_email_phone", param, checkuser)
        quit()

    if len(user) == 1:
        user = user[0][0]
    else:
        user = 0
    return user


def add_new_users(param):
    """
    Добавляет пользователей в базу данных
    :return: возвращает id добавленного пользователя
    """
    user = []
    LAST_NAME = param['LAST_NAME']
    FIRST_NAME = param['FIRST_NAME']
    if param['MIDDLE_NAME'] != "":
        MIDDLE_NAME = param['MIDDLE_NAME']
    else:
        MIDDLE_NAME = "NULL"

    if param.get('CITY_ID', "") != "":
        CITY_ID = param['CITY_ID']
    else:
        CITY_ID = "NULL"

    if param['TELEPHON'] != "":
        TELEPHON = param['TELEPHON']
    else:
        TELEPHON = "NULL"

    if param['EMAIL'] != "":
        EMAIL = param['EMAIL']
    else:
        EMAIL = "NULL"
    try:
        db = sqlite3.connect(DB_NAME)
        cursor = db.cursor()
        db.execute("INSERT INTO users(LAST_NAME,FIRST_NAME,MIDDLE_NAME,CITY_ID,TELEPHON,EMAIL)"
                   " VALUES ('" + LAST_NAME + "','" + FIRST_NAME + "','" + MIDDLE_NAME + "',"
                   + CITY_ID + ",'" + TELEPHON + "','" + EMAIL + "');")
        db.commit()
        db.close()
    except sqlite3.Error:
        logging.warning("add_new_users", param, "INSERT INTO users(LAST_NAME,FIRST_NAME,MIDDLE_NAME,CITY_ID,TELEPHON,EMAIL)"
                        " VALUES ('" + LAST_NAME + "','" + FIRST_NAME + "','" + MIDDLE_NAME + "',"
                        + CITY_ID + ",'" + TELEPHON + "','" + EMAIL + "');")
        quit()

    try:
        db = sqlite3.connect(DB_NAME)
        cursor = db.cursor()
        user = cursor.execute("SELECT max(id) FROM users WHERE LAST_NAME='" + LAST_NAME + "' AND FIRST_NAME='" + FIRST_NAME + "'").fetchall()
        db.close()
    except sqlite3.Error:
        logging.warning("add_new_users", param, "SELECT max(id) FROM users WHERE LAST_NAME='" + LAST_NAME + "' AND FIRST_NAME='" + FIRST_NAME + "'")
        quit()


    return user[0][0]


def add_comment(user, comment):
    """
    Добавляет комментарий в базу данных
    """
    try:
        db = sqlite3.connect(DB_NAME)
        db.execute("INSERT INTO comments(USER_ID,COMMENT)"
                   " VALUES (" + str(user) + ",'" + comment + "');")
        db.commit()
        db.close()
    except sqlite3.Error:
        logging.warning("add_comment", "INSERT INTO comments(USER_ID,COMMENT)"
                        " VALUES (" + str(user) + ",'" + comment + "');")
        quit()


def list_comments(comments):
    """
    Создает список комментариев для вставки в HTML документ
    """
    out = ''
    for comment in comments:
        _id = comment[0]
        _comment = comment[2]
        _first_name = comment[4]
        _last_name = comment[5]

        if comment[6] == None or comment[6] == "NULL":
            _middle_name = ""
        else:
            _middle_name = comment[6]

        if comment[8] == None or comment[8] == "NULL":
            _telepfon = ""
        else:
            _telepfon = comment[8]

        if comment[9] == None or comment[9] == "NULL":
            _email = ""
        else:
            _email = comment[9]

        if comment[12] == None or comment[12] == "NULL":
            _city = ""
        else:
            _city = comment[12]

        if comment[14] == None or comment[14] == "NULL":
            _region = ""
        else:
            _region = comment[14]

        out += "<tr>" \
               "<td>{0}</td>" \
               "<td>{1}</td>" \
               "<td>{2}</td>" \
               "<td>{3}</td>" \
               "<td>{4}</td>" \
               "<td>{5}</td>" \
               "<td>{6}</td>" \
               "<td>{7}</td>" \
               "<td><form action='/view/' method='post'>" \
               "<input type='hidden' size='0' name='id' value='{8}'/>"\
               "<input type='submit' value='Удалить'/>" \
               "</form></td>" \
               "</tr>".format(_last_name, _first_name, _middle_name, _region, _city, _telepfon, _email, _comment, _id)
    return out


def get_stat():
    """
    Получает статистику и формирует HTML тэги для вставки статистики в HTML документ
    """
    out = ''
    try:
        db = sqlite3.connect(DB_NAME)
        cursor = db.cursor()
        listregions = cursor.execute("SELECT r.ID,r.REGION, COUNT(r.REGION) FROM comments com"
                   " LEFT OUTER JOIN users u ON com.USER_ID = u.id"
                   " LEFT OUTER JOIN citys c ON u.CITY_ID = c.ID"
                   " LEFT OUTER JOIN regions r ON c.REGION_ID = r.ID"
                   " GROUP BY r.REGION HAVING COUNT(r.REGION) > 5").fetchall()
        db.close()
    except sqlite3.Error:
        logging.warning("get_stat", "SELECT r.ID,r.REGION, COUNT(r.REGION) FROM comments com"
                        " LEFT OUTER JOIN users u ON com.USER_ID = u.id"
                        " LEFT OUTER JOIN citys c ON u.CITY_ID = c.ID"
                        " LEFT OUTER JOIN regions r ON c.REGION_ID = r.ID"
                        " GROUP BY r.REGION HAVING COUNT(r.REGION) > 5")
        quit()

    for region in listregions:
        out += "<tr>" \
                    "<td>{0}</td>" \
                    "<td>{1}</td>" \
                    "<td>{2}</td>" \
               "</tr>".format(region[1], "", region[2])
        try:
            db = sqlite3.connect(DB_NAME)
            cursor = db.cursor()
            listcitys = cursor.execute("SELECT c.REGION_ID, c.CITY, COUNT(c.CITY) FROM comments com"
                                       " LEFT OUTER JOIN users u ON com.USER_ID = u.id"
                                       " LEFT OUTER JOIN citys c ON u.CITY_ID = c.ID"
                                       " LEFT OUTER JOIN regions r ON c.REGION_ID = r.ID"
                                       " GROUP BY c.ID"
                                       " HAVING c.REGION_ID ={0}".format(region[0])).fetchall()
            db.close()
        except sqlite3.Error:
            logging.warning("get_stat", "SELECT c.REGION_ID, c.CITY, COUNT(c.CITY) FROM comments com"
                                       " LEFT OUTER JOIN users u ON com.USER_ID = u.id"
                                       " LEFT OUTER JOIN citys c ON u.CITY_ID = c.ID"
                                       " LEFT OUTER JOIN regions r ON c.REGION_ID = r.ID"
                                       " GROUP BY c.ID"
                                       " HAVING c.REGION_ID ={0}".format(region[0]))
            quit()

        for city in listcitys:
            out += "<tr>" \
                   "<td>{0}</td>" \
                   "<td>{1}</td>" \
                   "<td>{2}</td>" \
                   "</tr>".format("", city[1], city[2])
    return out

def app(environ, start_response):
    """
    Функция для обработки входящего запроса. Проверяется метод и адрес по которому происходит вызов.
    Если верное сочетание метода и адреса не найдено, выдеатся ошибка 404

    """

    path = environ['PATH_INFO']
    method = environ['REQUEST_METHOD']
    req_param = raw_query_string_to_dict(environ['QUERY_STRING'])

    if method == 'GET' and path == '/comment/':
        out = ''

        try:
            db = sqlite3.connect(DB_NAME)
            cursor = db.cursor()
            regions = cursor.execute("""SELECT * FROM regions""").fetchall()
            db.close()
        except sqlite3.Error:
            logging.warning(method,path,"""SELECT * FROM regions""")
            quit()

        for region in regions:
            out += '<option value="{0}">{1}</option>'.format(region[0], str(region[1]))

        response_body = open('templates/comment.html', encoding='utf-8').read().replace("<@!!!!@>", out)
        start_response('200 OK', [('Content-type', 'text/html')])
        return [bytes(response_body, encoding='utf-8')]

    elif method == 'POST' and path == '/citys/':
        out = '<select name="CITY_ID" style="float:left;">'

        try:
            db = sqlite3.connect(DB_NAME)
            cursor = db.cursor()
            regions = cursor.execute("""SELECT * FROM citys WHERE REGION_ID=""" + str(req_param['REGION_ID']) + """;""").fetchall()
            db.close()
        except sqlite3.Error:
            logging.warning(method, path, """SELECT * FROM citys WHERE REGION_ID=""" + str(req_param['REGION_ID']) + """;""")
            quit()

        for region in regions:
            out += '<option value="{0}">{1}</option>'.format(region[0], str(region[2]))

        start_response('200 OK', [('Content-type', 'text/plain')])
        return [bytes(out, encoding='utf-8')]

    elif method == 'POST' and path == '/comment/':

        try:
            request_body_size = int(environ['CONTENT_LENGTH'])
            req_param = raw_query_string_to_dict(str(environ['wsgi.input'].read(request_body_size)).replace("b'", ""))
        except (TypeError, ValueError):
            logging.warning(method, path,"Ошибка при обработке параметров")
            quit()

        if req_param['TELEPHON'] != "" or req_param['EMAIL'] != "":
            check = check_db_users_email_phone(req_param)
            if check == 1:
                user = check
            else:
                user = add_new_users(req_param)
        else:
            user = add_new_users(req_param)

        add_comment(user, req_param['COMMENT'][:-1])
        start_response('302 Found', [('Location', environ['HTTP_REFERER'])])
        return [b'1']

    elif method == 'GET' and path == '/view/':

        try:
            db = sqlite3.connect(DB_NAME)
            cursor = db.cursor()
            comments = cursor.execute(
                """SELECT *
                   FROM comments com
                   LEFT OUTER JOIN users u ON com.USER_ID = u.id
                   LEFT OUTER JOIN citys c ON u.CITY_ID = c.ID
                   LEFT OUTER JOIN regions r ON c.REGION_ID = r.ID;""").fetchall()
            db.close()
        except sqlite3.Error:
            logging.warning(method, path, """SELECT *
                            FROM comments com
                            LEFT OUTER JOIN users u ON com.USER_ID = u.id
                            LEFT OUTER JOIN citys c ON u.CITY_ID = c.ID
                            LEFT OUTER JOIN regions r ON c.REGION_ID = r.ID;""")
            quit()

        out = list_comments(comments)
        response_body = open('templates/view.html', encoding='utf-8').read().replace("<@!!!!@>", out)
        start_response('200 OK', [('Content-type', 'text/html')])
        return [bytes(response_body, encoding='utf-8')]

    elif method == 'POST' and path == '/view/':
        try:
            request_body_size = int(environ['CONTENT_LENGTH'])
            req_param = raw_query_string_to_dict(str(environ['wsgi.input'].read(request_body_size)).replace("b'", ""))
        except (TypeError, ValueError):
            logging.warning(method, path, "Ошибка при обработке параметров")
            quit()

        try:
            db = sqlite3.connect(DB_NAME)
            cursor = db.cursor()
            cursor.execute("DELETE FROM comments WHERE id={0}".format(req_param["id"][:-1]))
            db.commit()
            db.close()
        except sqlite3.Error:
            logging.warning(method, path, "DELETE FROM comments WHERE id={0}".format(req_param["id"][:-1]))
            quit()

        start_response('302 Found', [('Location', environ['HTTP_REFERER'])])
        return [b'1']

    elif method == 'GET' and path == '/stat/':
        out = get_stat()
        response_body = open('templates/stat.html', encoding='utf-8').read().replace("<@!!!!@>", out)
        start_response('200 OK', [('Content-type', 'text/html')])
        return [bytes(response_body, encoding='utf-8')]

    else:
        response_body = open('templates/404.html').read()
        start_response('404 Not Found', [('Content-type', 'text/html')])
        return [bytes(response_body, encoding='utf-8')]

firstruncheck.check_file_bd()
httpd = make_server(HOST, PORT, app)
logging.info('Сервер запущен')
# Serve until process is killed
httpd.serve_forever()