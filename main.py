import sys
import pandas as pd
from crawler import PortalCrawler
from selenium import webdriver
from selenium.common.exceptions import NoSuchDriverException

if __name__ == "__main__":
    id, pw = '', ''

    if len(sys.argv) >= 3:
        id = sys.argv[1]
        pw = sys.argv[2]

        if not id and pw:
            print('사용방법: python main.py [한양인 id] [한양인 pw]')
            sys.exit(0)
    else:
        id = input('[한양인 id]를 입력해주세요: ')
        pw = input('[한양인 pw]를 입력해주세요: ')

    try:
        driver = webdriver.Chrome()
        driver.get("https://portal.hanyang.ac.kr/sso/lgin.do")

        # Store the ID of the original window
        original_window = driver.current_window_handle

        crawler = PortalCrawler(driver)

        if crawler.closeOtherWindows(original_window) != "success":
            print("Cannot close other windows")
            sys.exit(-1)

        if crawler.login(id, pw) != "success":
            print("Cannot login")
            sys.exit(-1)

        grade_by_semester = crawler.fetch_grade_by_semester()
        if not grade_by_semester:
            print("Nothing to crawl")
            sys.exit(-1)

        print("어떤 항목을 크롤링할까요?")
        print("0. 전체")
        for idx, semester in enumerate(grade_by_semester, 1):
            print(f"{idx:2d}. {semester}")

        selected_idx = -1
        while True:
            try:
                selected_idx = int(input("번호를 입력하세요: "))
                if selected_idx >= 0 and selected_idx <= len(grade_by_semester):
                    break
            except ValueError:
                pass
            print("잘못된 번호입니다. 다시 입력하세요")

        if selected_idx == 0:
            print(f"{0}. 전체를 선택하셨습니다.")
            total_df = None
            for idx in range(len(grade_by_semester)):
                df = crawler.crawl(idx)
                if total_df is None:
                    total_df = df
                else:
                    total_df = pd.concat([total_df, df], axis = 0)
            df = total_df
            filename = "전체 학기별 성적.xlsx"
            sheet_name = "전체 학기별 성적"
        else:
            print(f"{selected_idx}. {grade_by_semester[selected_idx - 1]}를 선택하셨습니다.")
            df = crawler.crawl(selected_idx - 1)

            filename = f"{grade_by_semester[selected_idx - 1]}.xlsx"
            sheet_name = grade_by_semester[selected_idx - 1]
            if len(sheet_name) > 31:
                sheet_name = f"{sheet_name[:28]}..."

        df.to_excel(
            excel_writer=filename,
            sheet_name=sheet_name,
            startrow=1, startcol=1,
            engine='xlsxwriter',
            index=False
        )
        print(f"{filename}으로 저장되었습니다")

    except NoSuchDriverException as e:
        print(f"예상 위치에서 Chrome driver를 찾을 수 없습니다")
        sys.exit(-1)