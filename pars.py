import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import re
from urllib.parse import unquote
import random
import json

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
    "Cookie": 'yandexuid=1035420701637843948; is_gdpr=0; is_gdpr_b=CKnvWhDVVCgC; _yasc=HMEENZAXae+nP4Cen1wSvs6whavpZ8Ky92WAfhaE5WieCEWMZbkve1yHJCEvPA==; i=7Oc1ZJ7ojl0BZbP1/0cB9Y6q87H5ONaKGebw0pHizpzrUE7HikeyAVt2F8bivEFX76+4mmdiAGWqcFz0FzP+Rkd7yEw=; yp=1639094984.mcv.0#1639094984.mcl.#1639094986.szm.1%3A1280x1024%3A1208x912#1639128698.mct.null#1641664044.los.1#1641664044.losc.0#1639138951.ln_tp.01; ymex=1953203956.yrts.1637843956; _ym_uid=1637843956402107824; _ym_d=1637843957; yabs-frequency=/5/0m000Fmogc400000/kMQH9C_nrN88H840/; skid=1600832651638380308; amcuid=7249327971638490991'
}
search = int(input('введите эффективность поиска: '))
def get_source_html(url):
    driver = webdriver.Firefox()
    driver.maximize_window()

    try:
        driver.get(url=url)
        time.sleep(3)
        SCROLL_PAUSE_TIME = 0.5
        y = 0
        lists = 0


        while lists <= search:
            # Scroll down to bottom
            y = y + 1080
            scroll = str(y)
            driver.execute_script(f"window.scrollTo(0, {scroll})")
            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)
            lists = lists + 1
        src = driver.page_source


    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()

    soup = BeautifulSoup(src, 'lxml')
    items_divs = soup.find_all("div", class_='minicard-item__container')

    urls = []
    for item in items_divs:
        item_url = item.find('a').get("href")
        urls.append(item_url)
    urls_list = [url.strip() for url in urls]

    result_list = []
    urls_count = len(urls_list)
    count = 1
    for url in urls_list:
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")

        try:
            item_name = soup.find('div', class_='pd-m').find("span", {"itemprop": "name"}).text.strip()
        except Exception as _ex:
            item_name = None

        item_phones_list = []
        try:
            item_phones =  soup.find("div", class_="service-phones-list").find_all("a", class_="js-phone-number")
            for phone in item_phones:
                item_phone = phone.get("href").split(":")[-1].strip()
                item_phones_list.append(item_phone)
            print(item_name, item_phone)
        except Exception as _ex:
            item_phones_list = None

        try:
            item_address = soup.find("address", class_="iblock").text.strip()
        except Exception as _ex:
            item_address = None

        try:
            item_site = soup.find(text=re.compile("Сайт|Официальный сайт")).find_next().text.strip()
        except Exception as _ex:
            item_site = None

        social_networks_list = []
        try:
            item_social_networks = soup.find(text=re.compile("Страница в соцсетях")).find_next().find_all("a")
            for sn in item_social_networks:
                sn_url = sn.get("href")
                sn_url = unquote(sn_url.split("?to=")[1].split("&")[0])
                social_networks_list.append(sn_url)
        except Exception as _ex:
            social_networks_list = None

        result_list.append(
            {
                "item_name": item_name,
                "item_url": url,
                "item_phones_list": item_phones_list,
                "item_address": item_address,
                "item_site": item_site,
                "social_networks_list": social_networks_list
            }
        )

        time.sleep(random.randrange(2, 5))

        if count % 10 == 0:
            time.sleep(random.randrange(5, 9))

        print(f"[+] Processed: {count}/{urls_count}")

        count += 1

    with open("result.json", "w") as file:
        json.dump(result_list, file, indent=4, ensure_ascii=False)

    return "[INFO] Data collected successfully!"

def main():
    get_source_html(
        url=input('Введите ссылку ZOONa: '))
    # print(get_items_urls(file_path="file_path"))
    # print(get_data(file_path="file_path"))


if __name__ == "__main__":
    main()
