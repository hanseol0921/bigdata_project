from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 웹 드라이버 경로 설정
service = Service('chromedriver.exe')  # chromedriver 경로를 설정해주세요.
driver = webdriver.Chrome(service=service)

# 네이버 월요 웹툰 URL
url = 'https://comic.naver.com/webtoon?tab=mon'

# 페이지 열기
driver.get(url)

# 페이지 로딩 대기 (필요에 따라 조정)
time.sleep(3)

# "인기순" 탭 클릭하기
try:
    # 인기순 탭 찾기 및 클릭
    popular_tab = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div/div[2]/div[1]/div[2]/ul/li[2]/a'))
    )
    popular_tab.click()
    time.sleep(3)  # 탭 변경 후 로딩 대기
except Exception as e:
    print(f"인기순 탭 클릭 오류: {e}")
    driver.quit()
    exit()

# 데이터를 저장할 리스트
webtoons_data = []

# 웹툰 항목을 감싸는 요소들을 찾기 (각 웹툰 정보가 포함된 li 요소들)
webtoon_items = driver.find_elements(By.CSS_SELECTOR, '#content > div > div > div > ul > li')

# 각 웹툰 정보 추출
for item in webtoon_items:
    try:
        # 타이틀 추출
        title_element = item.find_element(By.CSS_SELECTOR, '.ContentTitle__title--e3qXt .text')
        title = title_element.text if title_element else 'N/A'

        # 썸네일 이미지 URL 추출
        thumbnail_img = item.find_element(By.CSS_SELECTOR, 'img.Poster__image--d9XTI')
        thumbnail_url = thumbnail_img.get_attribute('src') if thumbnail_img else 'N/A'

        # 작가명 추출
        artist_element = item.find_element(By.CSS_SELECTOR, '.ContentAuthor__author_wrap--fV7Lo a')
        artist = artist_element.text if artist_element else 'N/A'

        # 평점 추출
        rating_element = item.find_element(By.CSS_SELECTOR, '.rating_area span')
        rating = rating_element.text if rating_element else 'N/A'

        # 추출한 데이터 저장
        webtoons_data.append({
            '썸네일 이미지': thumbnail_url,
            '타이틀': title,
            '작가명': artist,
            '평점': rating
        })
    
    except Exception as e:
        print(f"웹툰 정보 추출 중 오류 발생: {e}")

# 수집된 데이터 출력
for webtoon in webtoons_data:
    print(webtoon)

# 크롬 드라이버 종료
driver.quit()

<div id="root">
<div id="wrap">
<div class="content_wrap">
<div class="content" class="cotent">
<div class="component_wrap">
<ul class="ContentList__content_list--q5KXY">
<li class="item">
<div class="ContentList__info_area--bXx7n>
<a class="ContentTitle__title_area--x24vt" href="/webtoon/list?titled=758037&tab=mon">
<span class="ContentTitle__title--e3qXt"><span class="text">참교육</span></span>

셀레니움
크롬드라이버 설치
익스플로러에 exe파일 넣기
gitignore에 *.exe
