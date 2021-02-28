import sqlite3
from selenium import webdriver
from selenium.webdriver.android.webdriver import WebDriver
from selenium.webdriver.common.by import By

NAME_DB = 'shopping_list.db'

ADD_DATE = (('Транквилизатор дыхания', '666', '999'),
            ('Подтяжки для рта', '1337', '8'),
            ('Хурма', '15', '1488'),
            ('Поясная шляпа', '322', '5000'))


class DB:

    @staticmethod
    def create_db(name_db):
        conn = sqlite3.connect(name_db)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS shopping(
           what_by TEXT,
           count TEXT,
           price TEXT);
        """)
        conn.commit()
        print(f'Создан файл БД {name_db}\n')

    @staticmethod
    def insert_db(name_db, data_list):
        conn = sqlite3.connect(name_db)
        cur = conn.cursor()
        cur.executemany("INSERT INTO shopping VALUES(?, ?, ?);", data_list)
        conn.commit()
        print(f'Записанные данные в БД:')
        for row in data_list:
            print(row)
        print()

    @staticmethod
    def select_db(name_db):
        conn = sqlite3.connect(name_db)
        cur = conn.cursor()
        all_rows = cur.execute("SELECT * FROM shopping;")
        data_tuple = tuple(value for value in all_rows)
        conn.commit()
        print('Данные из БД:')
        for row in data_tuple:
            print(row)
        print()
        return data_tuple

    @staticmethod
    def delete_all_from_db(name_db):
        conn = sqlite3.connect(name_db)
        cur = conn.cursor()
        cur.execute("DELETE FROM shopping")
        conn.commit()


class Page:

    LOCATOR_BTN_OPEN = (By.ID, 'open')
    LOCATOR_INPUT_NAME = (By.ID, 'name')
    LOCATOR_INPUT_COUNT = (By.ID, 'count')
    LOCATOR_INPUT_PRICE = (By.ID, 'price')
    LOCATOR_BTN_ADD_NEW_RECORD = (By.ID, 'add')

    def __init__(self):
        self.driver: WebDriver = webdriver.Chrome('chromedriver.exe')
        self.driver.set_window_size(1450, 999)
        self.driver.get('http://checkme.kavichki.com/')

    @staticmethod
    def match_data_send_and_parsing(send_data, parsing_data):
        changes_data_send = tuple(set(send_data) - set(parsing_data))
        changes_data_parsing = tuple(set(parsing_data) - set(send_data))
        if changes_data_send and changes_data_parsing:
            print('Добавленные данные в таблицу НЕ совпадают с данными из БД!')
        else:
            print('Добавленные данные в таблицу совпадают с данными из БД')

    def start(self):
        DB.create_db(NAME_DB)
        data = self.parser_table()
        DB.insert_db(NAME_DB, data)
        self.add_values_in_table(ADD_DATE)
        changes_data = self.change_in_table()
        self.match_data_send_and_parsing(ADD_DATE, changes_data)
        DB.delete_all_from_db(NAME_DB)
        self.driver.close()

    def change_in_table(self):
        new_data_page = self.parser_table()
        data_db = DB.select_db(NAME_DB)
        changes_data = tuple(set(new_data_page) - set(data_db))
        changes_data = tuple(reversed(changes_data))
        if changes_data:
            print('Найдены новые строки в таблице на сайте:')
            for row in changes_data:
                print(row)
            print()
        else:
            print('Не найдено изменений в таблице на сайте:')
        return changes_data

    def parser_table(self):
        element = (By.TAG_NAME, 'table')
        table = self.driver.find_element(*element)
        tr = table.find_elements(*(By.TAG_NAME, 'tr'))
        head_elements = tr[0].find_elements(*(By.TAG_NAME, 'th'))
        heads = (head_elements.text for head_elements in head_elements)
        data = []
        print('Спарсенные данные из таблицы:')
        print(heads)
        for el in tr[1:]:
            td = el.find_elements(*(By.TAG_NAME, 'td'))
            data_tuple = tuple([td.text for td in td[:3] if td.text])
            data.append(data_tuple)
            print(data_tuple)
        print()
        return data

    def clear_inputs(self):
        self.driver.find_element(*self.LOCATOR_INPUT_NAME).clear()
        self.driver.find_element(*self.LOCATOR_INPUT_COUNT).clear()
        self.driver.find_element(*self.LOCATOR_INPUT_PRICE).clear()

    def add_value_in_table(self, name, count, price):
        self.driver.find_element(*self.LOCATOR_BTN_OPEN).click()
        self.clear_inputs()
        self.driver.find_element(*self.LOCATOR_INPUT_NAME).send_keys(name)
        self.driver.find_element(*self.LOCATOR_INPUT_COUNT).send_keys(price)
        self.driver.find_element(*self.LOCATOR_INPUT_PRICE).send_keys(count)
        self.driver.find_element(*self.LOCATOR_BTN_ADD_NEW_RECORD).click()
        self.clear_inputs()

    def add_values_in_table(self, values):
        print('Добавленные данные в таблицу:')
        for value in values:
            print(value)
            self.add_value_in_table(value[0], value[1], value[2])
        print()


if __name__ == '__main__':
    page = Page()
    page.start()
