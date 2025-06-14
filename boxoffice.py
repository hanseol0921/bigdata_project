import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
import urllib.request
import json
import re
import time
from bs4 import BeautifulSoup

class BoxOfficeViewer:
    
    def __init__(self, api_key=None):
        self.base_url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
        self.api_key = api_key
        self.target_date = None
        self.data = None
        
    def set_api_key(self, api_key): 
        self.api_key = api_key
        
    def set_date(self, date_str=None):
        if date_str:
            self.target_date = date_str
        else:
            yesterday = datetime.now() - timedelta(days=1)
            self.target_date = yesterday.strftime('%Y%m%d')
        
    def fetch_data(self):
        if not self.api_key:
            print("API 키가 설정되지 않았습니다. set_api_key() 메서드를 사용하여 API 키를 설정하세요.")
            return False
            
        if not self.target_date:
            self.set_date()
            
        params = {
            'key': self.api_key,
            'targetDt': self.target_date
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            self.data = response.json()
            return True
        except requests.exceptions.RequestException as e:
            print(f"데이터 요청 중 오류가 발생했습니다: {e}")
            return False
            
    def get_ranking(self):
        if not self.data:
            if not self.fetch_data():
                return []
        try:
            box_office_list = self.data['boxOfficeResult']['dailyBoxOfficeList']
            ranking_info = []
            for movie in box_office_list:
                ranking_info.append({
                    '순위': movie['rank'],
                    '영화명': movie['movieNm'],  # 영화 제목만 반환
                })
            return ranking_info
        except (KeyError, ValueError) as e:
            print(f"순위 정보 처리 중 오류가 발생했습니다: {e}")
            return []
            
    def get_ticket_sales_rate(self):
        if not self.data:
            if not self.fetch_data():
                return []
        try:
            box_office_list = self.data['boxOfficeResult']['dailyBoxOfficeList']
            total_sales = sum(int(movie['salesAmt']) for movie in box_office_list)
            ticket_sales_info = []
            for movie in box_office_list:
                sales_amount = int(movie['salesAmt'])
                sales_rate = (sales_amount / total_sales) * 100 if total_sales > 0 else 0
                ticket_sales_info.append({
                    '순위': movie['rank'],
                    '영화명': movie['movieNm'],
                    '예매율': f"{sales_rate:.2f}%",
                    '일일관객수': format(int(movie['audiCnt']), ',') + '명'
                })
            return ticket_sales_info
        except (KeyError, ValueError) as e:
            print(f"예매율 정보 처리 중 오류가 발생했습니다: {e}")
            return []
            
    def get_sales(self):
        if not self.data:
            if not self.fetch_data():
                return []
        try:
            box_office_list = self.data['boxOfficeResult']['dailyBoxOfficeList']
            sales_info = []
            for movie in box_office_list:
                sales_info.append({
                    '순위': movie['rank'],
                    '영화명': movie['movieNm'],
                    '일일매출액': format(int(movie['salesAmt']), ',') + '원',
                    '누적매출액': format(int(movie['salesAcc']), ',') + '원',
                    '스크린수': movie['scrnCnt'],
                    '상영횟수': movie['showCnt']
                })
            return sales_info
        except (KeyError, ValueError) as e:
            print(f"매출액 정보 처리 중 오류가 발생했습니다: {e}")
            return []
            
    def get_info_by_option(self, option):
        if option == 1:
            return self.get_ranking()
        elif option == 2:
            return self.get_ticket_sales_rate()
        elif option == 3:
            return self.get_sales()
        else:
            print("잘못된 옵션입니다. 1(순위), 2(예매율), 3(매출액) 중 하나를 선택하세요.")
            return []
            
    def to_dataframe(self, option):
        data = self.get_info_by_option(option)
        return pd.DataFrame(data)
    

    @staticmethod
    def normalize(text):
        return re.sub(r'\s+', '', text.strip().lower())

    def get_movie_info_by_name(self, movie_name):
        if not self.data:
            if not self.fetch_data():
                return None

        try:
            box_office_list = self.data['boxOfficeResult']['dailyBoxOfficeList']
            total_sales = sum(int(movie['salesAmt']) for movie in box_office_list)
            target_movie = None

            for movie in box_office_list:
                if self.normalize(movie_name) in self.normalize(movie['movieNm']):
                    target_movie = movie
                    break

            if target_movie:
                sales_amt = int(target_movie['salesAmt'])
                sales_rate = (sales_amt / total_sales * 100) if total_sales > 0 else 0
                return {
                    'movieCd': target_movie['movieCd'],
                    '영화명': target_movie['movieNm'],
                    '예매율': f"{sales_rate:.2f}%",
                    '일일매출액': format(sales_amt, ',') + '원',
                    '누적매출액': format(int(target_movie['salesAcc']), ',') + '원',
                    '스크린수': target_movie['scrnCnt'],
                    '상영횟수': target_movie['showCnt'],
                    '일일관객수': format(int(target_movie['audiCnt']), ',') + '명'
                }
            return None  
        except Exception as e:
            print("영화 정보 처리 중 오류:", e)
            return None
    def fetch_movie_info(self, movie_code):
        if not self.api_key:
            print("API 키가 설정되지 않았습니다.")
            return None
        
        url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json"
        params = {
            'key': self.api_key,
            'movieCd': movie_code
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            movie_data = response.json()
            movie_info = movie_data.get('movieInfoResult', {}).get('movieInfo', {})
            
            title = movie_info.get('movieNm', '정보 없음')
            directors = movie_info.get('directors', [])
            director_names = ', '.join(d.get('peopleNm', '') for d in directors) if directors else '정보 없음'
            actors = movie_info.get('actors', [])
            actor_names = ', '.join(a.get('peopleNm', '') for a in actors[:5]) if actors else '정보 없음'  # 최대 5명
            plot = movie_info.get('showTm', '상영시간 정보 없음')  # 줄거리는 API에 없고 상영시간만 제공
            open_dt = movie_info.get('openDt', '')
            if open_dt and len(open_dt) == 8:
                open_dt = f"{open_dt[:4]}년 {open_dt[4:6]}월 {open_dt[6:]}일"
            elif not open_dt:
                open_dt = '개봉일 정보 없음'
            
         # 줄거리 정보는 KOBIS API에 없으므로 "줄거리 정보 없음"으로 표시
            return {
                '제목': title,
                '감독': director_names,
                '출연': actor_names,
                '상영시간': plot + '분',
                '개봉일': open_dt,
            
            }
            
        except Exception as e:
            print("영화 상세 정보 조회 중 오류:", e)
            return None




def n_blog(search):
    client_id = "m6nZpyW187lm1c7iMKSH"
    client_secret = "OBrpyxklnJ"
    encText = urllib.parse.quote(search)
    url = "https://openapi.naver.com/v1/search/blog?query=" + encText # JSON 결과
    # url = "https://openapi.naver.com/v1/search/blog.xml?query=" + encText # XML 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    json_data = ""
    if(rescode==200):
        response_body = response.read()
        # print(response_body.decode('utf-8'))
        json_data = response_body.decode('utf-8')
    else:
        print("Error Code:" + rescode)

    # Parse the JSON data
    data = json.loads(json_data)

    # Extract the required information from the 'items' list
    extracted_list = []
    for item in data.get('items', []):   # 여기를 수정했습니다
        
        title = re.sub(r'<.*?>', '', item.get("title", ""))
        description = re.sub(r'<.*?>', '', item.get("description", ""))

        extracted_item = {
            "title": title,
            "link": item.get("link", ""),
            "description": description,
            "bloggername": item.get("bloggername", ""),
            "postdate": item.get("postdate", "")
        }
        extracted_list.append(extracted_item)
        
    return extracted_list





def main():
    API_KEY = "0dfd8752d1b4b76ed1d45011c6607d56"

    viewer = BoxOfficeViewer(api_key=API_KEY)
    viewer.set_date()  # 기본은 어제 날짜
    viewer.fetch_data()

    while True:
            date_input = input("조회할 날짜를 입력하세요 (예: 20250613): ").strip()
            if not re.match(r'^\d{8}$', date_input):
                print("날짜 형식이 올바르지 않습니다. 예: 20250613")
                continue

            viewer.set_date(date_input)
            if viewer.fetch_data():
                if not viewer.data['boxOfficeResult']['dailyBoxOfficeList']:
                    print("해당 날짜에는 박스오피스 데이터가 없습니다. 다른 날짜를 입력해주세요.")
                    continue
                break
            else:
                print("해당 날짜의 데이터를 불러오는 데 실패했습니다. 다시 입력해주세요.")

    while True:
        print("\n==== 박스오피스 정보 메뉴 ====")
        print("1. 영화 박스오피스 순위")
        print("2. 영화 박스오피스 정보 (예매율, 매출액)")
        print("3. 영화 정보")
        print("4. 영화 후기 검색 (네이버블로그)")
        print("0: 종료")
        print()
        choice = input("번호 입력: ")

        if choice == "0":
            print("프로그램을 종료합니다.")
            break


        elif choice == "1":
            df = viewer.to_dataframe(1)
            if df.empty:
                print("데이터가 없습니다.")
            else:
                print(f"\n=== 박스오피스 순위 ({viewer.target_date}) ===")
                for _, row in df.iterrows():
                    print(f"{row['순위']}위. {row['영화명']}")
            time.sleep(1)
               

        elif choice == "2":
            print()
            search_name = input("조회할 영화 제목을 입력하세요: ").strip()
            result = viewer.get_movie_info_by_name(search_name)

            if result:
                print(f"\n=== '{result['영화명']}'의 정보 ({viewer.target_date}) ===")
                print(f"예매율: {result['예매율']}")
                print(f"일일매출액: {result['일일매출액']}")
                print(f"누적매출액: {result['누적매출액']}")
                print(f"스크린수: {result['스크린수']}개")
                print(f"상영횟수: {result['상영횟수']}회")
                print(f"일일관객수: {result['일일관객수']}")
            else:
                print("입력한 영화가 해당 날짜 박스오피스 목록에 없습니다.")
            time.sleep(1)

        elif choice == "3":
            search_name = input("영화 제목을 입력하세요: ").strip()
            result = viewer.get_movie_info_by_name(search_name)

            if result:
                movie_code = result.get('movieCd')
                if movie_code:
                    info = viewer.fetch_movie_info(movie_code)
                    if info:
                        print(f"\n=== '{info['제목']}' 영화 상세 정보 ===")
                        print(f"감독: {info['감독']}")
                        print(f"출연: {info['출연']}","등")
                        print(f"상영시간: {info['상영시간']}")
                        print(f"개봉일: {info['개봉일']}")
                    else:
                        print("상세 정보를 가져오지 못했습니다.")
                else:
                    print("해당 영화의 코드가 없습니다.")
            else:
                print("입력한 영화가 해당 날짜 박스오피스 목록에 없습니다.")
            time.sleep(1)

        elif choice == "4":
            print("\n영화 후기 검색 (네이버 블로그)")
            search = input("검색할 영화 제목 입력: ")
            blog_results = n_blog(search)

            if blog_results:
                print(f"\n=== '{search}' 관련 블로그 글 ===")
                for item in blog_results:
                    print(f"제목: {item['title']}")
                    print(f"링크: {item['link']}")
                    print(f"작성자: {item['bloggername']}")
                    print(f"작성일: {item['postdate']}")
                    print("-" * 40)
            else:
                print("블로그 검색 결과가 없습니다.")
            time.sleep(1)

        else:
            print("올바른 번호를 입력해주세요.")

if __name__ == "__main__":
    main()

