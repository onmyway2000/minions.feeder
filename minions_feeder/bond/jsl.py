import os
import time
import pandas as pd
import akshare as ak
from datetime import datetime

from minions_common.common.context import Context
from selenium import webdriver


class JSLConvertibleBondLoader:
    def __init__(self):
        self.__context = Context()
        self.__logger = self.__context.get_logger()
        self.__jsl_username = self.__context.get_config().get("minions.jsl", "user_name")
        self.__jsl_password = self.__context.get_config().get("minions.jsl", "password")
        self.__data_file = os.path.join(self.__context.get_data_path(), 'jsl_bond_df.csv')

    def get_bonds_from_jsl(self):
        df = pd.read_csv(self.__data_file, index_col=0, dtype={"bond_id": str, "stock_id": str})
        return df

    def load_bonds_from_jsl_with_retry(self):
        if os.path.exists(self.__data_file):
            df = pd.read_csv(self.__data_file, index_col=0)
            dt = datetime.now().replace(hour=9, minute=25, second=0, microsecond=0)
            if pd.to_datetime(df['datetime'].values[0]) > dt:
                return None

        last_ex = None
        for i in range(3):
            try:
                self.load_bonds_from_jsl()
                return "Successfully load bonds from jsl"
            except Exception as ex:
                last_ex = ex
                self.__logger.exception("Failed to load bond from jsl with retry={0}".format(i))
        raise last_ex

    def load_bonds_from_jsl(self):
        self.__logger.info("Start load bond from jsl")

        # options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        # driver = webdriver.Chrome(chrome_options=options)
        # driver = webdriver.Chrome()
        driver = webdriver.PhantomJS()
        driver.get('https://www.jisilu.cn/account/login/')
        time.sleep(2)
        user_name_control = driver.find_element_by_id("aw-login-user-name")
        user_name_control.send_keys(self.__jsl_username)
        time.sleep(0.5)
        password_control = driver.find_element_by_id("aw-login-user-password")
        password_control.send_keys(self.__jsl_password)
        time.sleep(0.5)
        agreement_check = driver.find_element_by_id("agreement_chk")
        agreement_check.click()
        time.sleep(0.5)
        login_control = driver.find_element_by_id("login_submit")
        login_control.click()
        time.sleep(2)
        driver.get('https://www.jisilu.cn/data/cbnew/#cb')
        time.sleep(2)
        cookie_string = self.__get_cookie_string(driver)
        df = ak.bond_cov_jsl(cookie=cookie_string)
        if len(df) > 100:
            df['datetime'] = datetime.now()
            df.to_csv(self.__data_file)
        else:
            raise Exception("Failed to load fully bond info from jsl")

        self.__logger.info("Successfully load bond from jsl")
        return df

    def __get_cookie_string(self, driver):
        cookie_list = driver.get_cookies()
        cookie_string = ""
        for cookie in cookie_list:
            cookie_string += cookie['name'] + "=" + cookie['value'] + ";"
        self.__logger.info("Try to load jsl bond list by login,got cookie:{}".format(cookie_string))
        return cookie_string
