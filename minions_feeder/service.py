from minions_common.common.context import Context
from minions_common.rpc.thrift import GeneralCommandService, ReturnType

from minions_feeder.bond.em import EMConvertibleBondLoader
from minions_feeder.bond.jsl import JSLConvertibleBondLoader


class FeederService(GeneralCommandService):
    def __init__(self):
        context = Context()
        endpoint = context.get_config().get("minions.feeder", "endpoint_feeder")
        super().__init__(endpoint)

        self._add_command_handler("get", lambda target: self.__get_function_map[target](), [str], ReturnType.DataFrame)
        self._add_command_handler("load", lambda target: self.__load_function_map[target](), [str], ReturnType.Message)

        self.__jsl_loader = JSLConvertibleBondLoader()
        self.__em_loader = EMConvertibleBondLoader()
        self.__get_function_map = {"jsl": self.__jsl_loader.get_bonds_from_jsl,
                                   "em": self.__em_loader.get_bonds_from_east_money}
        self.__load_function_map = {"jsl": self.__jsl_loader.load_bonds_from_jsl_with_retry,
                                    "em": self.__em_loader.load_bonds_from_east_money_with_retry}
