import pandas as pd
import logging
import time

from data_preprocess import preprocess_dataframe
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

logging.basicConfig(filename="portal_grade_crawler.log", level=logging.INFO)

class PortalCrawler:
    def __init__(self, driver):
        self.driver = driver

    def closeOtherWindows(self, original_window):
        # Wait for the new window or tab
        # WebDriverWait(driver, 3).until(EC.number_of_windows_to_be(2))

        # Loop through until we find a new window handle
        for window_handle in self.driver.window_handles:
            if window_handle != original_window:
                self.driver.switch_to.window(window_handle)
                self.driver.close()
                self.driver.switch_to.window(original_window)

        return "success"

    def login(self, id, pw):
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#hyinContents > div.login_box > form > div > fieldset > p.btn_login > a")))
        login_btn = self.driver.find_element(By.CSS_SELECTOR, "#hyinContents > div.login_box > form > div > fieldset > p.btn_login > a")

        if not login_btn:
            return "cannot access to login page"

        user_id = self.driver.find_element(By.CSS_SELECTOR, "#userId")
        user_pw = self.driver.find_element(By.CSS_SELECTOR, "#password")

        if not user_id:
            print("ID 입력란을 찾을 수 없습니다")
            return "user_id not found"
        if not user_pw:
            print("PW 입력란을 찾을 수 없습니다")
            return "password is empty"
        if not login_btn:
            print("로그인 버튼을 찾을 수 없습니다")
            return "login_btn not found"

        user_id.send_keys(id)
        user_pw.send_keys(pw)
        login_btn.click()
        
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#btn_cancel")))
        btn_cancel = self.driver.find_element(By.CSS_SELECTOR, "#btn_cancel")
        if btn_cancel is not None:
            btn_cancel.click()
        
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#lnb > ul > li.M002489 > ul > li.M008728 > a")))
        # 학기별 성적 조회 클릭
        link = self.driver.find_element(By.CSS_SELECTOR, "#lnb > ul > li.M002489 > ul > li.M008728 > a").get_attribute('href')
        self.driver.get(link)

        return "success"

    def fetch_grade_by_semester(self):
        # 성적이 존재하는 학기 전체 갯수 가져오기
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#gdDtl1 > tbody > tr")))
        semester_elements = self.driver.find_elements(By.CSS_SELECTOR, "#gdDtl1 > tbody > tr")
        semesters = [
            table_row_item.find_element(By.ID, "yearGradeTerm").text
            for table_row_item in semester_elements
        ]
        print(semesters)
        return semesters

    def crawl(self, idx):
        columns = [
            "년도-학년-학기",
            "이수구분",
            "학수번호",
            "과목명",
            "학점",
            "취득점수",
            "최종점수",
            "평점",
            "등급",
            "성취도평가",
            "재수강여부",
            "재수강과목"
        ]
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, f"#gdDtl1 > tbody > tr:nth-child({idx+1})")))
        self.driver.find_element(By.CSS_SELECTOR, f"#gdDtl1 > tbody > tr:nth-child({idx+1})").click()
        WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#tblMain_pop > tbody > tr")))

        time.sleep(1)
        rows = []
        logging.info(f"[크롤링 시작]")
        for tr in self.driver.find_elements(By.CSS_SELECTOR, "#tblMain_pop > tbody > tr"):
            row_data = []
            for td in tr.find_elements(By.TAG_NAME, "td"):
                row_data.append(td.text)
            rows.append(row_data)
        logging.info(f"[크롤링 종료]")
        logging.info(f"[크롤링한 데이터 변환중]")
        
        df = pd.DataFrame.from_records(rows, columns=columns)
        logging.info(f"[크롤링한 데이터 변환완료]")
        
        WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#btn_Cancel")))
        self.driver.find_element(By.CSS_SELECTOR, "#btn_Cancel").click()
        time.sleep(1)

        logging.info(f"[크롤링한 데이터 전처리 시작]")
        df = preprocess_dataframe(df)
        logging.info(f"[크롤링한 데이터 전처리 완료]")
        return df