import json
from datetime import datetime
from copy import deepcopy
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from src.auchan_parser import collect_products, make_driver
from src.utils import choose_spb, choose_moscow, more_products

MAIN_DICT = {
    "shop": {
        "name": "Auchan",
        "url": "https://www.auchan.ru/",
    },
    "category": {
        "name": "plombir",
        "url": "https://www.auchan.ru/catalog/morozhenoe/plombir/"
    },
    "city": list(),
}
PRODUCTS_DICT = {
    "name": "",
    "count_items": 0,
    "results": list(),
}


def parse(city: str, json_dict: dict) -> None:
    time_start = datetime.now()
    total_processed_products, total_item, total_duplicate_counter,\
        total_out_of_stock = 0, 0, 0, 0
    page = 1

    driver = make_driver()

    driver.get('https://www.auchan.ru/catalog/morozhenoe/plombir/')

    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.TAG_NAME, "html")))

    if city == "m":
        city = choose_moscow(driver=driver)
    else:
        city = choose_spb(driver=driver)

    counter_by_web = driver.find_element(By.CLASS_NAME, "css-1wy2lqx").text
    json_dict["name"] = city
    more = False

    with open("./index_selenium_auchan.html", "w", encoding="utf-8") as file:
        file.write(driver.page_source)

    items, counter, duplicate_counter, out_of_stock = \
        collect_products(json_dict, page)

    total_processed_products += counter
    total_item += items
    total_duplicate_counter += duplicate_counter
    total_out_of_stock += out_of_stock

    while not more:
        page += 1
        more = more_products(driver, page)
        if more:
            break

        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.TAG_NAME, "html")))

        with open(
                "./index_selenium_auchan.html", "w", encoding="utf-8"
        ) as file:
            file.write(driver.page_source)

        items, counter, duplicate_counter, out_of_stock = \
            collect_products(json_dict, page)

        if items is True:
            break
        total_processed_products += counter
        total_item += items
        total_duplicate_counter += duplicate_counter
        total_out_of_stock += out_of_stock

    json_dict["count_items"] = total_processed_products

    MAIN_DICT["city"].append(json_dict)
    time_end = datetime.now() - time_start
    print(f"Всего получено карточек товаров: {total_item}\n"
          f"Всего добавлено товаров в json: {total_processed_products}\n"
          f"Всего найдено дубликатов в выдаче: {total_duplicate_counter}\n"
          f"Всего товаров нет в наличии: {total_out_of_stock}\n"
          f"Товаров заявлено в выдаче веб-сайте: "
          f"{counter_by_web.replace('(', '').replace(')', '')}")
    print(f"Время работы скрипта: {time_end}")


def main() -> None:
    print("Поиск по Москве")
    parse("m", deepcopy(PRODUCTS_DICT))
    print("#############################")
    print("Поиск по Санкт-Петербургу")
    parse("s", deepcopy(PRODUCTS_DICT))
    current_time = datetime.now().strftime("%d_%m_%Y_%H_%M")
    with open(
            f"./jsons/auchan_plombir_{current_time}.json", "w",
            encoding="utf-8"
    ) as file:
        json.dump(MAIN_DICT, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
