import unittest

from minions_common.auto.image import image_from_array

from minions_feeder.service import FeederService


class TestFeederService(unittest.TestCase):
    def test(self):
        thrift = FeederService().thrift
        client = thrift.make_client(host="192.168.1.160", timeout=1 * 60 * 1000)

        self.__execute(thrift, client, "load jsl")
        self.__execute(thrift, client, "load em")
        # self.__execute(thrift, client, "get jsl")
        # self.__execute(thrift, client, "get em")
        client.close()

    def __execute(self, thrift, client, command):
        print()
        print("Command:" + str(command))
        try:
            result = client.execute(command)
            print("Message:" + str(result.message))
            print("DataFrame:" + str(result.dataframe))
            if result.image is not None:
                image_from_array(result.image).show()

        except thrift.ServiceInternalError as se:
            print("ServiceInternalError:" + str(se))
        except Exception as ex:
            print("Exception" + str(ex))

    def test_exception_processing(self):
        try:
            raise Exception("Some Exception")
        except Exception as ex:
            print(ex.args)


if __name__ == '__main__':
    unittest.main()
