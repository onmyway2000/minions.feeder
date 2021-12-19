import unittest

import pandas as pd

from datetime import datetime

from minions_feeder.bond.em import EMConvertibleBondLoader


class TestEMConvertibleBondLoader(unittest.TestCase):
    def test_load_bonds_from_east_money(self):
        loader = EMConvertibleBondLoader()
        df = loader.load_bonds_from_east_money()
        print(df)

        bond_id_not_to_market = df[df['time_to_market'].isnull() | (
                pd.to_datetime(df['time_to_market']) > (datetime.now() - pd.Timedelta(days=2)))]
        print(bond_id_not_to_market)

    def test_load(self):
        loader = EMConvertibleBondLoader()
        message = loader.load_bonds_from_east_money_with_retry()
        print(message)


if __name__ == '__main__':
    unittest.main()
