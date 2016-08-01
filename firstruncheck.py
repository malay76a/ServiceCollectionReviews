import configparser
import logging
import os
import sqlite3

# подключаемся к файлу с логами
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# В данном блоке загружается информация из конфигурациооного файла
try:
    conf = configparser.RawConfigParser()
    conf.read("app.cfg")
    DB_NAME = conf.get("database", "db_name") + ".db"
except Exception:
    logging.warning('Ошибка при подключении к файлу конфигурации')
    quit()

def check_file_bd():
    """
    Проверка на наличие файла базы данных. Если файла нет, то попытка его создания
    :return: булево значение результат проверки
    """

    if not os.path.isfile(DB_NAME):
        db = sqlite3.connect(DB_NAME)
        try:
            with open('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()
            logging.info('Файл базы данных и внутренняя структура созданны успешно')
            return True
        except sqlite3.Error:
            logging.warning('Ошибка при создании файла базы данных')
            return False
        db.close()
    else:
        logging.info('Файл базы данных существует')
        return True
