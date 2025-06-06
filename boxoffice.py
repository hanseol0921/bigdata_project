import requests
import pandas as pd
from datetime import datetime, timedelta

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

def main():
    # 여기에 본인의 KOBIS API 키 입력!
    API_KEY = "0dfd8752d1b4b76ed1d45011c6607d56"

    viewer = BoxOfficeViewer(api_key=API_KEY)
    viewer.set_date()  # 기본은 어제 날짜
    viewer.fetch_data()

    while True:
        print("\n==== 박스오피스 정보 메뉴 ====")
        print("1: 박스오피스 순위")
        print("2: 예매율")
        print("3: 매출액")
        print("0: 종료")
        choice = input("번호 입력: ")

        if choice == "0":
            print("프로그램을 종료합니다.")
            break

        if choice in ["1", "2", "3"]:
            df = viewer.to_dataframe(int(choice))
            if df.empty:
                print("데이터가 없습니다.")
            else:
                # 영화명 앞뒤 공백 제거
                if '영화명' in df.columns:
                    df['영화명'] = df['영화명'].str.strip()
                print(df.to_string(index=False))
        else:
            print("올바른 번호를 입력해주세요.")

if __name__ == "__main__":
    main()
