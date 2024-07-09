from loguru import logger
from ebm.model.database_manager import DatabaseManager, ScurveParameters



database_manager = DatabaseManager()

param = database_manager.get_s_curve_params_per_building_category_and_condition("House", 'Demolition')
logger.debug(f'{param.building_category=}, {param.condition=}')
print(param)