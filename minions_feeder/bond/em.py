import os

import numpy as np
import pandas as pd

import akshare as ak
from datetime import datetime
from minions_common.common.context import Context


class EMConvertibleBondLoader:
    def __init__(self):
        self.__context = Context()
        self.__logger = self.__context.get_logger()
        self.__data_file = os.path.join(self.__context.get_data_path(), 'east_money_bond_df.csv')

    def get_bonds_from_east_money(self):
        df = pd.read_csv(self.__data_file, index_col=0)
        return df

    def load_bonds_from_east_money_with_retry(self):
        if os.path.exists(self.__data_file):
            df = pd.read_csv(self.__data_file, index_col=0)
            dt = datetime.now().replace(hour=9, minute=25, second=0, microsecond=0)
            if pd.to_datetime(df['datetime'].values[0]) > dt:
                return None

        last_ex = None
        for i in range(3):
            try:
                self.load_bonds_from_east_money()
                return "Successfully load bonds from east money"
            except Exception as ex:
                last_ex = ex
                self.__logger.exception("Failed to load bond from east money with retry={0}".format(i))
        raise last_ex

    def load_bonds_from_east_money(self):
        self.__logger.info("Start load bond from east money")
        df = ak.bond_zh_cov()
        df.loc[df['交易场所'] == 'CNSESH', '债券代码'] = "SHSE." + df.loc[df['交易场所'] == 'CNSESH', '债券代码']
        df.loc[df['交易场所'] == 'CNSESZ', '债券代码'] = "SZSE." + df.loc[df['交易场所'] == 'CNSESZ', '债券代码']
        df.loc[df['交易场所'] == 'CNSESH', '正股代码'] = "SHSE." + df.loc[df['交易场所'] == 'CNSESH', '正股代码']
        df.loc[df['交易场所'] == 'CNSESH', '正股代码'] = "SZSE." + df.loc[df['交易场所'] == 'CNSESZ', '正股代码']

        df = df[['债券代码', '债券简称', '正股代码', '正股简称', '转股价', '上市时间', '债现价', '正股价', '转股价值', '转股溢价率']]
        df.loc[df['转股价'] == '-', '转股价'] = np.nan
        df.loc[df['正股价'] == '-', '正股价'] = np.nan
        df.loc[df['债现价'] == '-', '债现价'] = np.nan
        df.loc[df['转股价值'] == '-', '转股价值'] = np.nan
        df.loc[df['转股溢价率'] == '-', '转股溢价率'] = np.nan
        df.dropna(inplace=True)
        df.loc[df['上市时间'] == '-', '上市时间'] = np.nan
        df.sort_values(['上市时间'], inplace=True, ascending=False)
        df.reset_index(inplace=True, drop=True)

        df.rename(columns={'债券代码': 'bond_id', '债券简称': 'bond_nm', '正股代码': 'stock_id', '正股简称': 'stock_nm',
                           '转股价': 'convert_price', '上市时间': 'time_to_market', '债现价': 'price', '正股价': 'sprice',
                           '转股价值': 'convert_value', '转股溢价率': 'premium_rt'}, inplace=True)
        df.insert(0, column="datetime", value=datetime.now())
        df.to_csv(self.__data_file)
        self.__context.log_data_frame("em_bond_df", df, with_datetime=False)
        self.__logger.info("Successfully load bond from east money")
        return df
