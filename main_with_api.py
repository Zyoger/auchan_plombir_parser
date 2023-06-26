import json
import requests

from copy import deepcopy
from datetime import datetime

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
MOSCOW = {
    "name": "moscow",
    "merchant_id": 1,
    "region_id": 1,
    "gashop": "001_Mitishchi",
}
SAINT_PETERSBURG = {
    "name": "saint-petersburg",
    "merchant_id": 102,
    "region_id": 2,
    "gashop": "102_Parnas",
}


def fetch(url, params):
    headers = params["headers"]
    data = params["body"]
    result = requests.post(url, headers=headers, data=data)
    return result.status_code, result.json()


def get_url_and_params(
        merchant_id: int = 1, gashop: str = "001",
        region_id: int = 1, page: int = 1,
):
    url = f"https://www.auchan.ru/v1/catalog/products?merchantId={merchant_id}&page={page}&perPage=100&orderField=discountPercent&orderDirection=desc"
    params = {"headers": {
        "accept": "application/json, text/plain, */*",
        "accept-language": "ru,en;q=0.9",
        "content-type": "application/json;charset=UTF-8",
        "sec-ch-ua": "\"Chromium\";v=\"112\", \"YaBrowser\";v=\"23\", \"Not:A-Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie": f"methodDelivery_=1; mindboxDeviceUUID=45ea4f84-b79c-43a1-8a1e-e2c9441522b2; directCrm-session=%7B%22deviceGuid%22%3A%2245ea4f84-b79c-43a1-8a1e-e2c9441522b2%22%7D; _ym_uid=168645544919092079; _ym_d=1686455449; tmr_lvid=21e0c08c615044d07fcbc16252f07c2c; tmr_lvidTS=1686455449152; rrpvid=554118422355439; _userGUID=0:liqw14wj:w5e3DTEXPCjD8HZKZ0hEOAjP4culah79; _ymab_param=liSpeDuIyBgx2alj_7W3_3romGZYZisJmf7q2MiOKLOQpHJhF3cz-3L2Ht-Xi3Vv1dfTL49xM46BJVn2rg7kYjQHT4g; rcuid=648544997016a2f896ecef3e; haveChat=true; _clck=yslv34|2|fcd|0|1257; rrlevt=1686537267099; digi_uc=W1sidiIsIjI3NjUxMSIsMTY4NjUzNzI2Njc2OV0sWyJ2IiwiNTIzMjIiLDE2ODY1MzcyMjMxMzldLFsidiIsIjcxNjEzOCIsMTY4NjUzNzIxMTMxNl0sWyJ2IiwiMzczOTUxIiwxNjg2NTM3MTkxMzA2XSxbInYiLCI1MTAyOSIsMTY4NjUzNTMyNzc0MF0sWyJ2IiwiMjcyNzk2IiwxNjg2NTM1Mjc2MTk5XSxbInYiLCI0ODQwODYiLDE2ODY1MzA3NTkzNTBdLFsidiIsIjQ4NTIzNCIsMTY4NjUyNTU5NjYzMF0sWyJ2IiwiNTk4NTgiLDE2ODY0NjE5MzM4MTNdLFsidiIsIjk4NDcyOCIsMTY4NjQ2MTg3OTA2MF1d; region_id={region_id}; merchant_ID_={merchant_id}; _GASHOP={gashop}; isEreceiptedPopupShown_=true; qrator_ssid=1687657610.076.ndrOEhC5d2xfW38t-fghddltvj3uoe3anli7l2usdqaqlu9up; dSesn=91e09a19-1c8f-285b-2af7-1cab5125df03; _dvs=0:ljarrmy7:Nq9w0W1I3VXlJVHiQm5AcKB4aP5opse4; _ym_isad=1; qrator_jsid=1687657620.183.oy9WgA9PGWbC3pUL-o6vm389b6hi9smbrlgid6cmhm7hi1uo8; tmr_detect=0%7C1687658812736",
        "Referer": "https://www.auchan.ru/catalog/morozhenoe/plombir/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    },
        "body": "{\"filter\":{\"category\":\"plombir_2\",\"promo_only\":false,\"active_only\":true,\"cashback_only\":false}}",
    }

    return url, params


def parse_city_merchant(city: dict):
    merchant_id = city["merchant_id"]
    gashop = city["gashop"]
    region_id = city["region_id"]
    page = 1

    count_items = 0

    url, params = get_url_and_params(
        merchant_id=merchant_id,
        gashop=gashop,
        region_id=region_id,
        page=page,
    )

    city_items = deepcopy(PRODUCTS_DICT)
    city_items["name"] = city["name"]

    while True:
        status_code, response = fetch(url, params)

        if status_code != 200:
            print(f"Не удалось получить товары. Статус код: {status_code}")
            break

        items = response["items"]
        count_items += len(response["items"])

        for item in items:
            item_dict: dict = {
                "id": item["id"],
                "title": item["title"],
                "url": f"https://www.auchan.ru/product/{item['code']}",
                "regular_price": item["oldPrice"]["value"] if item.get("oldPrice") else item["price"]["value"],
                "sale_price": item["price"]["value"] if item.get("discount") else "",
                "brand": item["brand"]["name"],
            }

            city_items["results"].append(item_dict)

        if count_items >= response["activeRange"]:
            city_items["count_items"] = count_items
            break

        page += 1

        url, params = get_url_and_params(
            merchant_id=merchant_id,
            gashop=gashop,
            region_id=region_id,
            page=page,
        )

    MAIN_DICT["city"].append(city_items)


def main():
    current_time = datetime.now().strftime("%d_%m_%Y_%H_%M")
    parse_city_merchant(MOSCOW)
    parse_city_merchant(SAINT_PETERSBURG)
    with open(
            f"./jsons/auchan_plombir_{current_time}.json", "w",
            encoding="utf-8"
    ) as file:
        json.dump(MAIN_DICT, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
