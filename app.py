from minions_common.common.context import Context
from minions_common.common.schedule import ScheduleService

from minions_feeder.service import FeederService

context = Context("minions.feeder")
logger = context.get_logger()

logger.info("Start to launch Feeder Service")
feeder_service = FeederService()
feeder_service.start()
logger.info("Finish to launch Feeder Service")

logger.info("Start to launch schedule Service")
scheduler = ScheduleService()
scheduler.start()
logger.info("Finish to launch schedule Service")

feeder_service.join()
