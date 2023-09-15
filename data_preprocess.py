import pandas as pd

def convert_to_year(year_hakyun_hakkyi):
    year, _, _ = year_hakyun_hakkyi.strip().split("-")
    return int(year[:-1])

def convert_to_hakkyi(year_hakyun_hakkyi):
    _, _, hakkyi = year_hakyun_hakkyi.strip().split("-")
    return hakkyi[:-2]

def convert_to_kind(kind):
    return "전공" if "전공" in kind else "교양기타"

def convert_to_grade(grade):
    if grade == 'P':
        return "PASS"
    # A0, B0, C0, D0
    if len(grade) >= 2 and grade[1] == '0':
        return grade[0]
    return grade

def preprocess_dataframe(df):
    new_df = pd.DataFrame()
    new_df["수강년도"] = df["년도-학년-학기"].apply(convert_to_year)
    new_df["학기"] = df["년도-학년-학기"].apply(convert_to_hakkyi)
    new_df["과목명"] = df["과목명"]
    new_df["과목유형"] = df["이수구분"].apply(convert_to_kind)
    new_df["취득학점"] = df["학점"].apply(float).apply(int)
    new_df["성적"] = df["등급"].apply(convert_to_grade)
    new_df["재수강여부"] = df["재수강여부"]
    return new_df