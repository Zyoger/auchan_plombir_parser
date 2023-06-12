import json
import os

from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

shop_base_url = "https://www.auchan.ru/"


def make_driver() -> Chrome:
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': '''
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
          '''
    })

    return driver


def collect_products(products_dict: dict, page: int):
    with open("./index_selenium_auchan.html", "r", encoding="utf-8") as file:
        source = file.read()

    soup = BeautifulSoup(source, "lxml")

    duplicate_counter = 0
    counter = 0
    out_of_stock = 0
    added_products = 0

    products_inner = soup.find(class_="css-i0ae9m css-1jbfeca-Layout")

    items = products_inner.find_all(class_="css-n9ebcy-Item")
    total_item = len(items)

    if items[0].find(class_="productCard hidden css-whfrs5"):
        os.remove("./index_selenium_auchan.html")
        return True, 0, 0, 0

    for product in items:
        in_stock = product.find(class_="linkToPDP hidden css-1kl2eos")
        counter += 1

        if in_stock:
            # print(f"[INFO] обработал {counter}/{total_item} "
            #       f"на странице {page}")
            out_of_stock += 1
            continue

        product_json = json.loads(
            product.find(
                "script"
            ).text
        )

        title_scope = product.find(class_="linkToPDP active css-1kl2eos")
        url = f'{shop_base_url}{title_scope["href"][1::]}'

        price_scope = product.find(
            class_="productCardPriceData active css-1lxwves")
        regula_price = price_scope.find(class_="active css-1j9wd4t")

        if regula_price:
            regula_price = regula_price.text.split()[0]
            sale_price = ""
        else:
            regula_price = price_scope.find(
                class_="active css-1u1qt12"
            ).text.split()[0]
            sale_price = price_scope.find(
                class_="active css-3g832i"
            ).text.split()[0]

        product_dict = {
            "id": product["data-offer-id"],
            "title": product_json["name"],
            "url": url,
            "regular_price": regula_price,
            "sale_price": sale_price,
            "brand": product_json["brand"],
        }
        red_flag = False
        for prod in products_dict["results"]:
            if prod["id"] == product["data-offer-id"]:
                # print(f"[INFO] обработал {counter}/{total_item} "
                #       f"на странице {page}")
                # print("Есть дубликаты")
                # print(f"{prod['id']}")
                # print(f"{prod['title']}")
                red_flag = True
                break

        if red_flag:
            duplicate_counter += 1
            continue
        products_dict["results"].append(product_dict)

        added_products += 1
        # print(f"[INFO] обработал {counter}/{total_item} "
        #       f"на странице {page}")

    count_results = total_item - out_of_stock
    products_dict["count_items"] = count_results

    os.remove("./index_selenium_auchan.html")

    return total_item, added_products, duplicate_counter, out_of_stock
