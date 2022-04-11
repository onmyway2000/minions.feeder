import unittest

from minions_feeder.bond.jsl import JSLConvertibleBondLoader


class Test(unittest.TestCase):
    def test_load(self):
        loader = JSLConvertibleBondLoader()
        message = loader.load_bonds_from_jsl_with_retry()
        print(message)

    def test_direct_load(self):
        loader = JSLConvertibleBondLoader()
        df = loader.load_bonds_from_jsl()
        print(df)


if __name__ == '__main__':
    unittest.main()
