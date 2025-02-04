import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re



class archer():
    def __init__(self, gender, bowstyle, ageroup, standardround, face, score):
        self.gender = gender
        self.bowstyle = bowstyle
        self.agegroup = ageroup
        self.standardround = standardround
        self.face = face
        self.score = score
        self.handicap = ""
        self.classification = ""

        self.get_info()


    def get_info(self):
        not_allowed = ['L and R 300', '20yd - 252', 'L&R300']
        if self.standardround in not_allowed:
            self.handicap = "NA"
            self.classification = "NA"
        else:
            self.set_dropboxes()
            text_box = driver.find_element(By.ID, "score")
            text_box.send_keys(self.score)
            self.calculate()
            text_box.clear()


    def set_dropboxes(self):
        self.__use_dropbox('gender', self.gender)
        self.__use_dropbox('bowstyle', self.bowstyle)
        self.__use_dropbox('agegroup', self.agegroup)
        self.__use_dropbox('standardround', self.standardround)


    def __use_dropbox(self, id, input):
        dropdown = driver.find_element(By.ID, id)
        select = Select(dropdown)
        select.select_by_value(input)

    def calculate(self):
        wait = WebDriverWait(driver, 10)
        button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Calculate')]")))
        button.click()
        handicap_element = driver.find_element("id", "parCalculatedHandicap")
        handicap_text = handicap_element.text
        text = re.findall(r"(?<== )[0-9]*", handicap_text)[0]
        self.handicap = text
        classification_element = driver.find_element("id", "parClassificationForScore")
        classification_text = classification_element.text
        classification_text = classification_text.split("\n")[0]
        text = re.findall(r"(?<== ).*", classification_text)[0]
        self.classification = text


def main():
    INFILE_PATH = "testing.csv"
    OUTFILE_PATH = "testing.csv"

    df = pd.read_csv(INFILE_PATH)
    df.dropna(how='all',inplace=True)

    gender_dict = {
        'M':'Men',
        'F':'Women'
    }

    age_dict = {
        'Snr':'Senior',
        'U21':'U21'
    }

    compound_dict = {
        "Portsmouth": "Portsmouth (Triple Face) Compound",
        "WA18": "WA 18m (Triple Face) Compound",
        "Bray I": "Bray I (Triple Face) Compound",
        "Worcester": "Worcester (5-Spot)"
    }

    multi_dict = {
        'Portsmouth':'Portsmouth (Triple Face)',
        'WA18': "WA 18m (Triple Face)",
        "Bray I":"Bray I (Triple Face)"
    }

    global driver
    driver = webdriver.Chrome()
    driver.get('https://www.archerygeekery.co.uk/hc/calculator.php')
    for index, row in df.iterrows():
        handicap = row['Handicap']
        if not pd.isna(handicap):
            continue
        gender = gender_dict[row['Gender']]
        bowstyle = row['Bow Style'].strip()
        agegroup = age_dict[row['Cat']].strip()
        standardround = row['Round'].strip()
        face = row['Face']
        score = str(int(row['Score']))
        if bowstyle == 'Compound':
            standardround = compound_dict[standardround]
        elif face == "Multi" and bowstyle != "Compound":
            standardround = multi_dict[standardround]
        elif standardround == "WA18":
            standardround = "WA 18m"
        archer_obj = archer(gender, bowstyle, agegroup, standardround, face, score)
        df.loc[index, "Handicap"] = archer_obj.handicap
        df.loc[index, "Classification"] = archer_obj.classification
        time.sleep(1)

    df.to_csv(OUTFILE_PATH, index=False)

main()
