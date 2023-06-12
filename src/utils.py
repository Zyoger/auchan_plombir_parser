from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


def search_and_click_button(driver: Chrome, xpath: str) -> None:
    try:
        button = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located(
                (By.XPATH, xpath))
        )
    except (TimeoutException, NoSuchElementException):
        print(f"Не удалось найти кнопку по xpath: {xpath}")
    else:
        button.click()


def choose_moscow(driver: Chrome):
    search_and_click_button(
        driver=driver, xpath='//*[@id="currentRegionName"]'
    )
    search_and_click_button(
        driver=driver, xpath='//*[@id="regions"]'
    )
    search_and_click_button(
        driver=driver, xpath='//*[@id="regions"]/option[1]'
    )
    driver.implicitly_wait(1)
    search_and_click_button(
        driver=driver, xpath='//*[@id="selectShop"]'
    )
    return "Moscow"


def choose_spb(driver: Chrome) -> str:
    search_and_click_button(
        driver=driver, xpath='//*[@id="currentRegionName"]'
    )
    search_and_click_button(
        driver=driver, xpath='//*[@id="regions"]'
    )
    search_and_click_button(
        driver=driver, xpath='//*[@id="regions"]/option[2]'
    )
    driver.implicitly_wait(1)
    search_and_click_button(
        driver=driver, xpath='//*[@id="selectShop"]'
    )
    return "Saint Petersburg"


def more_products(driver, page):
    try:
        WebDriverWait(driver, 1).until(
            ec.presence_of_element_located(
                (By.XPATH, '//*[@id="main"]/main/div/div/p'))
        )
    except TimeoutException:
        driver.get(
            f"https://www.auchan.ru/catalog/morozhenoe/plombir/?page={page}")
        return False
    else:
        return True
