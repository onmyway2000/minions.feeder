import os
import platform
import time

import pandas as pd
from datetime import datetime

from minions_common.common.context import Context
from selenium import webdriver

from minions_feeder.bond.jsl_fix import bond_cov_jsl


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

        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        if platform.platform().startswith("Windows-10"):
            executable_path = os.path.join(self.__context.get_resource_path(), "geckodriver.exe")
        else:
            executable_path = "geckodriver"
        service_log_path = os.path.join(self.__context.get_logging_path(), "geckodriver.log")
        driver = webdriver.Firefox(executable_path=executable_path, service_log_path=service_log_path, options=options)

        # driver = webdriver.ChromiumEdge(
        #     executable_path=os.path.join(self.__context.get_resource_path(), "msedgedriver.exe"))
        # driver = webdriver.PhantomJS()
        # driver = webdriver.Remote(command_executor="http://127.0.0.1:4444/wd/hub",
        #                           desired_capabilities=DesiredCapabilities.CHROME)

        self.__execute_login(driver)
        cookie_string = self.__get_cookie_string(driver)
        driver.close()
        time.sleep(2)
        df = bond_cov_jsl(cookie=cookie_string)
        if len(df) > 100:
            df.insert(0, column="datetime", value=datetime.now())
            df.to_csv(self.__data_file)
            self.__context.log_data_frame("jsl_bond_df", df, with_datetime=False)
            self.__logger.info("Successfully load bond from jsl")
        else:
            raise Exception("Failed to load fully bond info from jsl,not fully loaded")
        return df

    def __execute_login(self, driver):
        driver.implicitly_wait(2)
        driver.get('https://www.jisilu.cn/account/login/')
        user_name_control = \
            driver.find_elements_by_xpath("/html/body/div[3]/div/div/div[1]/div[1]/div[3]/form/div[2]/input")[0]
        user_name_control.send_keys(self.__jsl_username)
        password_control = \
            driver.find_elements_by_xpath("/html/body/div[3]/div/div/div[1]/div[1]/div[3]/form/div[3]/input")[0]
        password_control.send_keys(self.__jsl_password)
        remember_check = \
            driver.find_elements_by_xpath("/html/body/div[3]/div/div/div[1]/div[1]/div[3]/form/div[5]/div[1]/input")[0]
        remember_check.click()
        agreement_check = \
            driver.find_elements_by_xpath("/html/body/div[3]/div/div/div[1]/div[1]/div[3]/form/div[5]/div[2]/input")[0]
        agreement_check.click()
        login_control = \
            driver.find_elements_by_xpath("/html/body/div[3]/div/div/div[1]/div[1]/div[3]/form/div[6]/a")[0]
        login_control.click()
        driver.get("https://www.jisilu.cn/web/data/cb/list")

    def __get_cookie_string(self, driver):
        cookie_list = driver.get_cookies()
        cookie_string = ""
        for cookie in cookie_list:
            cookie_string += cookie['name'] + "=" + cookie['value'] + ";"
        self.__logger.info("Try to load jsl bond list by login,got cookie:{}".format(cookie_string))
        return cookie_string
