import os
import time
import requests
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class GoogleImageScraper:
    def __init__(self, keyword, limit):
        self.keyword = keyword
        self.limit = limit
        self.save_path = f"./{keyword}"
        self.success_count = 0
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def run(self):
        chrome_options = Options()
        
        # 자동화 제어 신호 숨기기
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        # 4. 언어 및 화면 크기 설정
        chrome_options.add_argument("lang=ko_KR")
        chrome_options.add_argument("window-size=1920,1080")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })

        try:
            # 구글 이미지 검색 접속
            driver.get(f"https://www.google.com/search?q={self.keyword}&tbm=isch")
            time.sleep(random.uniform(2.5, 4.0))

            # 스크롤 동작
            for _ in range(2):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1.5, 2.5))

            # 이미지 후보 추출
            thumbnails = driver.find_elements(By.CSS_SELECTOR, "img.Q4LuWd, img.rg_i")
            print(f">>> 발견된 이미지 후보: {len(thumbnails)}개") 

            for i, thumb in enumerate(thumbnails):
                if self.success_count >= self.limit: 
                    break
                
                try:
                    # 썸네일 클릭
                    driver.execute_script("arguments[0].click();", thumb)
                    time.sleep(random.uniform(2.0, 3.5)) 

                    # 원본 이미지 URL 추출
                    img_elements = driver.find_elements(By.CSS_SELECTOR, "img.sFlh5c.pT0Scc")
                    
                    for img in img_elements:
                        src = img.get_attribute('src')
                        if src and src.startswith('http') and not src.startswith('https://encrypted'):
                            # 이미지 다운로드 및 저장
                            response = requests.get(src, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                            if response.status_code == 200:
                                file_name = f"{self.keyword}_{self.success_count + 1}.jpg"
                                with open(os.path.join(self.save_path, file_name), 'wb') as f:
                                    f.write(response.content)
                                self.success_count += 1
                                print(f"[{self.success_count}/{self.limit}] {file_name} 저장 완료") 
                                break
                except Exception: 
                    continue

        finally:
            # 결과 요약
            print(f"\n[최종 결과] 성공: {self.success_count} / 목표: {self.limit}")
            driver.quit()

if __name__ == "__main__":
    search_word = input("검색어 입력: ").strip() 
    try:
        count_input = input("수집 개수 입력: ").strip() 
        if not count_input.isdigit(): 
            raise ValueError
        count = int(count_input)
        
        scraper = GoogleImageScraper(search_word, count)
        scraper.run() 
    except ValueError:
        print("에러: 숫자를 입력해야 합니다.")