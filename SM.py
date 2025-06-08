from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# 크롬 드라이버 경로 지정 (혹은 환경변수 PATH에 추가)
CHROMEDRIVER_PATH = '/path/to/chromedriver'

BASE_URL = 'https://www.smentertainment.com/artist/'

# 크롬 드라이버 실행 설정
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 창을 띄우지 않음
service = Service(CHROMEDRIVER_PATH)

def get_driver():
    return webdriver.Chrome(service=service, options=options)

def get_all_artists():
    print("\n[1] SM 아티스트 모두 보기")
    driver = get_driver()
    driver.get(BASE_URL)
    time.sleep(3)  # JS 로딩 기다리기

    names = driver.find_elements(By.CSS_SELECTOR, ".name")
    for name in names:
        print("- " + name.text)
    driver.quit()


def get_all_groups():
    print("\n[2] SM 그룹 모두 보기")
    driver = get_driver()
    driver.get(BASE_URL)
    time.sleep(3)

    groups = set()
    items = driver.find_elements(By.CSS_SELECTOR, ".name")
    for item in items:
        text = item.text
        if text.isupper() or text.isalpha():
            groups.add(text)
    for group in sorted(groups):
        print("- " + group)
    driver.quit()


def search_artist_info(name):
    print(f"\n[3] '{name}' 아티스트 정보 검색 중...")
    driver = get_driver()
    driver.get(BASE_URL)
    time.sleep(3)

    artist_cards = driver.find_elements(By.CSS_SELECTOR, ".artistWrap")

    found = False
    for card in artist_cards:
        artist_name = card.find_element(By.CLASS_NAME, "name").text
        if name.lower() in artist_name.lower():
            print(f"\n✅ 아티스트: {artist_name}")
            link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
            print("🔗 상세 링크:", link)
            driver.get(link)
            time.sleep(2)

            profile_items = driver.find_elements(By.CSS_SELECTOR, ".profileInfoWrap li")
            for item in profile_items:
                print("- " + item.text)
            found = True
            break

    if not found:
        print("❌ 해당 아티스트를 찾을 수 없습니다.")
    driver.quit()


def main():
    while True:
        print("\n===== SM 엔터테인먼트 아티스트 메뉴 =====")
        print("1. SM 아티스트 모두 보기")
        print("2. SM 그룹 모두 보기")
        print("3. SM 아티스트 정보 찾기")
        print("0. 종료")
        choice = input("번호를 선택하세요: ")

        if choice == '1':
            get_all_artists()
        elif choice == '2':
            get_all_groups()
        elif choice == '3':
            name = input("아티스트 이름을 입력하세요: ")
            search_artist_info(name)
        elif choice == '0':
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 입력입니다. 다시 선택하세요.")

if __name__ == "__main__":
    main()

