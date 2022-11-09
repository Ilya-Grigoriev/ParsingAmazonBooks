import pytesseract
import time
import subprocess
from urllib.request import urlretrieve
from selenium import webdriver
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def save_html(driver) -> None:
    with open('test.html', mode='w') as html:
        html.write(driver.print_page())


def get_image_text(image_url: str) -> str:
    urlretrieve(image_url, 'page.jpg')
    p = subprocess.Popen(['tesseract', 'page.jpg', 'page'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    file = open('page.txt', 'r', encoding='utf-8')
    print(file.read().strip('\n'))


pytesseract.pytesseract.tesseract_cmd = input(
    'Enter the path to tesseract.exe: ')
url_book = input(
    'Enter link to the book where the Look-inside function with viewing images is available: ')
chrome_options = Options()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)
try:
    driver.get(url_book)
    time.sleep(2)
    driver.find_element(by=By.ID, value='litb-canvas-click-wrapper').click()

    checking = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, 'litb-read-frame')))

    frame = driver.find_element(By.ID, 'litb-read-frame')
    ind = 0
    action = ActionChains(driver)
    scroll_origin = ScrollOrigin.from_element(frame)
    driver.switch_to.frame(frame)

    checking = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, 'litb-renderer')))

    render = driver.find_element(by=By.ID, value='litb-renderer')
    images = render.find_elements(
        by=By.TAG_NAME, value='img')
    driver.switch_to.default_content()
    move_y = 905
    move_pos = -100000
    while True:
        moving = action.scroll_from_origin(scroll_origin, 0, move_y)
        moving.perform()

        driver.switch_to.frame(frame)
        render = driver.find_element(by=By.ID, value='litb-renderer')
        images_2 = render.find_elements(
            by=By.TAG_NAME, value='img')
        driver.switch_to.default_content()

        print(f'Number images: {len(images_2)}')
        print(f'Page index: {ind}')
        ind += 1
        if len(images_2) > len(images):
            move_y = -move_y
            move_pos = -move_pos
            images = images_2
            moving = action.scroll_from_origin(scroll_origin, 0, move_pos)
            moving.perform()
            ind = 0
        if ind == len(images):
            break
        time.sleep(0.15)
    driver.switch_to.frame(frame)
    render = driver.find_element(by=By.ID, value='yj-html-render')
    images = render.find_elements(
        by=By.TAG_NAME, value='img')

    print('Printing pages:')
    for page, image in enumerate(images, start=1):
        image_url = image.get_attribute('src')
        print(f'Page: {page}')
        get_image_text(image_url)
    print('End of printing')
except Exception as e:
    raise e
finally:
    driver.close()
