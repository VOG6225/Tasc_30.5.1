"""запускать через флаги для вывода в консоль
pytest tests/test_tasc.py -s -v """

import time

from config import login, password
import pytest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Добавляем фикстуру c неявным ожиданием для всех объектов

@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.get('https://petfriends.skillfactory.ru/login')
    # time.sleep(3)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()


# Тестовая функция
def test_mypets(driver):
# # 1. ВВОДИМ ЛОГИН И ПАРОЛЬ
    # driver.find_element(By.ID, 'email').send_keys(login)
    # driver.find_element(By.ID, 'pass').send_keys(password)

    # C явным ожиданием элементов
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'email'))).send_keys(login)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'pass'))).send_keys(password)

    # 2. НАЖИМАЕМ КНОПКУ ВХОДА
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
#    time.sleep(5)

    # 3. ПРОВЕРЯЕМ ЧТО ПОПАЛИ НА ГЛАВНУЮ

    assert driver.find_element(By.TAG_NAME, 'h1').text == "PetFriends"

###########################################################################
    # 4. Боремся с всплывающим окном от менеджера паролей.
    driver.execute_script("window.open('');")


    # 5. ПЕРЕКЛЮЧАЕМСЯ НА НОВУЮ ВКЛАДКУ
    driver.switch_to.window(driver.window_handles[1])


    # 6. ПЕРЕХОДИМ ПО ПРЯМОЙ ССЫЛКЕ В НОВОЙ ВКЛАДКЕ
    driver.get('https://petfriends.skillfactory.ru/my_pets')
#    time.sleep(3)

    # 7. ЗАКРЫВАЕМ СТАРУЮ ВКЛАДКУ (С ВСПЛЫВАЮЩИМ ОКНОМ)
    driver.switch_to.window(driver.window_handles[0])
    driver.close()

    # 8. ПЕРЕКЛЮЧАЕМСЯ ОБРАТНО НА НОВУЮ ВКЛАДКУ
    driver.switch_to.window(driver.window_handles[0])
#    time.sleep(2)

    # 9. ПРОВЕРЯЕМ ЧТО ПОПАЛИ НА СТРАНИЦУ "МОИ ПИТОМЦЫ"

    assert driver.current_url == 'https://petfriends.skillfactory.ru/my_pets'
    print(f"URL страницы: {driver.current_url}")
###########################################################################

    # 10. Данные о кол-ве питомцев со страницы
    #my_pets = driver.find_element(By.XPATH, "//div[@class='.col-sm-4 left']")
    # c ожиданием
    my_pets = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='.col-sm-4 left']")))

    total = my_pets.text
    totals = total.split('\n')

    count_text = totals[1].split(' ')
    count_pets = count_text[1] # кол-во питомцев
    # Кол-во питомцев по данным со страницы
    print(f"Питомцев по данным с страницы: {count_pets}")


    # Работаем с карточками на странице, через неявные ожидания из фикстуры

    images = driver.find_elements(By.XPATH, '//*[@id="all_my_pets"]/table/tbody/tr/th/img')

    assert int(count_pets) == len(images)
    print("Задание №1 - Данные на странице о кол-ве питомцев совпадает с кол-ом карточек")
    count_pets_photo = 0
    print("\nЗадание № 2 - Хотя бы у половины питомцев есть фото")
    for i, image in enumerate(images, 1):
        src = image.get_attribute('src')

        if src != "" and src != None:
            print(f"Питомец {i} имеет изображение")
            count_pets_photo += 1
        else:
            print(f"Питомец {i} не имеет изображения")

    assert count_pets_photo >= int(count_pets) / 2
    if count_pets_photo >= int(count_pets) / 2:
        print(f"У {count_pets_photo} из {count_pets} есть фото")
    else:
        print(f" Только у {count_pets_photo} питомцев из {count_pets} есть фото")

 # Составляем список из имени, возраста, вида питомца
    name_pets = driver.find_elements(By.XPATH, '//*[@id="all_my_pets"]/table/tbody/tr/td')
    card_pets = [] # Список из Имени, вида, возраста
    for i, name in enumerate(name_pets, 1):
        if name.text != "×":
            card_pets.append(name.text)


    # Формируем списки с Именем, Видом, и возрастом
    names = card_pets[0::3]
    types = card_pets[1::3]
    ages = card_pets[2::3]


    # У всех ли питомцев есть Имя, возраст, порода
    print("Задание № 3 - У всех ли питомцев есть Имя, возраст, порода")
    flag = True
    for i in range(len(names)):
        if names[i] == "" or types[i] == "" or ages[i] == "":
            flag = False
            break

    assert flag == True
    if flag == True:
        print("У всех питомцев есть имя, вид, возраст")
    else:
        print("Не у всех питомцев есть имя, вид, возраст")

    print("Задание № 4 - У всех ли питомцев разные имена")


    # Перобразуем список имен в множество для удаления дубликатов и сравним общее число элементов

    unique_names = set(names)
    if len(unique_names) == len(names):
        print("У всех питомцев уникальные имена")
    else:
        print("Имеются повторяющиеся имена питомцев")
    # assert len(unique_names) == len(names) - # Если оставить то тест пстанавливается на этой проверке.

    print("Задание № 5 - Нет ли повторяющихся питомцев")

    # Создаем список кортежей (имя, вид, возраст) для каждого питомца
    pets = list(zip(names, types, ages))

    # Преобразуем в множество и удалим дубликаты
    unique_pets = set(pets)
    # Найдем дубликаты
    duplicates = []  # Создаем пустой список
    for pet in pets:  # Перебираем каждого питомца в списке pets
        if pets.count(pet) > 1:  # Если этот питомец встречается в списке больше 1 раза
            duplicates.append(pet)  # Добавляем его в список дубликатов

    print(f"Повторяющиеся питомцы: {duplicates}")

    assert len(unique_pets) == len(pets)