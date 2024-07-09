from loguru import logger
from ebm.model.database_manager import DatabaseManager, ScurveParameters



database_manager = DatabaseManager()

param = database_manager.get_scurve_params_per_building_category("House", 'Demolition')
logger.debug(f'{param.building_category=}, {param.condition=}')
print(param)