import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
import re
import csv

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/39.0.2171.95 Safari/537.36 '
}


def parse_category():
    links_category = []
    r = requests.get('https://moto-gk.ru/elektroinstrument', headers=headers)
    soup = BeautifulSoup(r.text, features='lxml')
    # Получаем список всех категорий электроинструмента
    for i in soup.find_all('div', class_='sub-group-block'):
        links_category.append('https://moto-gk.ru/' + i.find('a')['href'])
    # Если есть подкатегории, то добавляем их в список
    for link in links_category:
        r = requests.get(link, headers=headers)
        soup = BeautifulSoup(r.text, features='lxml')
        if soup.find('div', class_='sub-groups'):
            links_category.pop(links_category.index(link))
            for i in soup.find_all('div', class_='sub-group-block'):
                links_category.append('https://moto-gk.ru/' + i.find('a')['href'])
    return links_category


def parse_items():
    wb = Workbook()
    ws = wb.active
    test_list = []
    for i in parse_category():
        r = requests.get(i, headers=headers)
        soup = BeautifulSoup(r.text, features='lxml')
        pagination = soup.find('div', class_='navigator')

        # TODO He's alive!!!
        if pagination:
            # Вытаскиваем количество страниц, если меньше 5 добавляем + 2, в проитивном случае + 1
            # не имею понятия, каког хрена так
            if int(pagination.find_all('a')[-2].text) < 5:
                pages_num = int(pagination.find_all('a')[-2].text) + 2
            else:
                pages_num = int(pagination.find_all('a')[-2].text) + 1

            for page in range(1, pages_num):
                r = requests.get(i + '?page=' + str(page), headers=headers)
                soup = BeautifulSoup(r.text, features='lxml')
                for j in soup.find_all('div', class_='main-part'):
                    try:
                        test_list.append(
                            [
                                j.find('div', class_='code').text.strip(),
                                j.find('h3').text.strip(),
                                j.find('p', class_='shortDesc').text.strip(),
                                j.find('div', class_='price').text.strip()
                            ]
                        )
                    except AttributeError:
                        pass

        # TODO в блоке else - рабочий код
        else:
            for j in soup.find_all('div', class_='main-part'):
                try:
                    test_list.append(
                        [
                            j.find('div', class_='code').text.strip(),
                            j.find('h3').text.strip(),
                            j.find('p', class_='shortDesc').text.strip(),
                            j.find('div', class_='price').text.strip()
                         ]
                    )
                except AttributeError:
                    pass
    for fex in test_list:
        ws.append(fex)
    wb.save('moto.xlsx')


parse_items()
