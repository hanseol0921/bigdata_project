from selenium import webdriver
from selenium.webdriver.common.by import By # By import
from selenium.webdriver.chrome.service import Service # Service import (for newer Selenium)
import time

# 네이버 월요 웹툰 URL
url = 'https://comic.naver.com/webtoon?tab=mon'

# 웹 드라이버 경로 설정 (다운로드한 ChromeDriver 경로를 여기에 입력하세요)
# 예: service = Service('/path/to/chromedriver')
# 만약 ChromeDriver를 시스템 PATH에 추가했다면 아래 service=... 라인은 주석 처리하거나 제거합니다.
# driver = webdriver.Chrome() # PATH에 추가된 경우

# 또는 Service 객체를 사용하여 경로 지정 (최신 Selenium 권장 방식)
try:
    # 다운로드 받은 크롬 드라이버 경로를 입력하세요.
    # 예: service = Service('C:/WebDriver/chromedriver.exe') # Windows
    # 예: service = Service('/Users/yourname/webdriver/chromedriver') # macOS/Linux
    service = Service('chromedriver.exe') # <-- 이 부분을 수정하세요.
    driver = webdriver.Chrome(service=service)
except Exception as e:
    print(f"웹 드라이버 초기화 오류: {e}")
    print("ChromeDriver 경로를 확인하거나 시스템 PATH에 추가했는지 확인하세요.")
    exit() # 오류 발생 시 프로그램 종료

# 웹 페이지 열기
driver.get(url)

# 페이지 로딩을 기다릴 시간을 설정 (필요에 따라 조절)
time.sleep(3) # 페이지의 동적 콘텐츠 로딩을 위해 충분히 기다립니다.

# 데이터를 저장할 리스트
webtoons_data = []

try:
    # //* 웹툰 목록을 감싸는 요소들을 찾습니다.
    # //* 아래 셀렉터는 예시이며, 실제 네이버 웹툰 HTML 구조를 보고 정확히 바꿔야 합니다.
    # //* 보통 각 웹툰 하나하나를 나타내는 li 또는 div 요소를 찾습니다.
    # //* 개발자 도구(F12)로 웹툰 목록 부분을 검사하여 적절한 CSS 셀렉터를 찾으세요.
    webtoon_items = driver.find_elements(By.CSS_SELECTOR, '#content > div:nth-child(1) > ul') # 예시 셀렉터

    print(f"총 {len(webtoon_items)}개의 웹툰을 찾았습니다.")

    # 각 웹툰 요소에서 정보 추출
    for item in webtoon_items:
        try:
            # 썸네일 이미지 주소 추출
            # 썸네일 이미지는 img 태그의 src 속성에 있습니다.
            # 이미지를 감싸는 요소나 이미지 태그 자체의 셀렉터를 찾습니다.
            thumbnail_img = item.find_element(By.CSS_SELECTOR, '#content > div:nth-child(1) > ul > li:nth-child(1) > a > div > img') # 예시 셀렉터
            thumbnail_url = thumbnail_img.get_attribute('src') if thumbnail_img else 'N/A'

            # 타이틀 추출
            # 타이틀은 보통 a 태그의 텍스트입니다.
            # 타이틀 요소를 감싸는 셀렉터와 타이틀 a 태그의 셀렉터를 찾습니다.
            title_element = item.find_element(By.CSS_SELECTOR, '#content > div:nth-child(1) > ul > li:nth-child(1) > div > a > span > span') # 예시 셀렉터
            title = title_element.text if title_element else 'N/A'

            # 작가명 추출
            # 작가명은 보통 a 또는 span 태그의 텍스트입니다.
            # 작가명 요소를 감싸는 셀렉터와 작가명 태그의 셀렉터를 찾습니다.
            artist_element = item.find_element(By.CSS_SELECTOR, '#content > div:nth-child(1) > ul > li:nth-child(1) > div > div.ContentAuthor__author_wrap--fV7Lo > a') # 예시 셀렉터 (여러 작가일 수 있음)
            # 여러 작가일 경우 join을 사용하거나 첫 번째 작가만 가져옵니다.
            artist = artist_element.text if artist_element else 'N/A'


            # 평점 추출
            # 평점은 보통 strong 또는 em 태그의 텍스트입니다.
            # 평점 요소를 감싸는 셀렉터와 평점 태그의 셀렉터를 찾습니다.
            rating_element = item.find_element(By.CSS_SELECTOR, '#content > div:nth-child(1) > ul > li:nth-child(1) > div > div.rating_area > span > span') # 예시 셀렉터
            rating = rating_element.text if rating_element else 'N/A'


            # 추출한 데이터 저장
            webtoons_data.append({
                '썸네일 이미지 주소': thumbnail_url,
                '타이틀': title,
                '작가명': artist,
                '평점': rating
            })

        except Exception as e:
            # 특정 웹툰 처리 중 오류 발생 시 건너뛰거나 로깅
            print(f"웹툰 정보 추출 중 오류 발생: {e}")
            # 오류 발생 시 해당 웹툰은 데이터에 추가하지 않거나 'N/A' 등으로 표시

finally:
    # 웹 드라이버 종료
    driver.quit()

# 수집된 데이터 출력 (또는 파일로 저장)
for webtoon in webtoons_data:
    print(webtoon)

# 데이터를 CSV 파일 등으로 저장하고 싶다면 pandas 라이브러리 사용을 고려해 볼 수 있습니다.
# import pandas as pd
# df = pd.DataFrame(webtoons_data)
# df.to_csv('naver_monday_webtoons.csv', index=False, encoding='utf-8-sig')
# print("\n데이터를 'naver_monday_webtoons.csv' 파일로 저장했습니다.")