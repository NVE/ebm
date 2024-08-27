# Introduction 
TODO: Give a short introduction of your project. Let this section explain the objectives or the motivation behind this project. 

# Getting Started
TODO: Guide users through getting your code up and running on their own system. In this section you can talk about:

[Detailed developer documentation found here (Norwegian)](docs/README.md)

## 1. Installation process

 `python -m pip install energibruksmodell-0.7.3.tar.gz`


## 2. Software dependencies
  - pandas
  - loguru
  - rich
   
  See also [requirements.txt](requirements.txt)
## 3. Run

### Running as a script
```cmd
calculate-area-forecast
```

### Running as a module

```cmd
python3 -m ebm
```

### Running as code
```python

from pprint import pprint as pp
import pandas as pd
from ebm.model import BuildingCategory, Buildings, DatabaseManager
from ebm.model.construction import ConstructionCalculator

years = [y for y in range(2010, 2050 + 1)]

database_manager = DatabaseManager()
building_category = BuildingCategory.HOUSE
buildings = Buildings.build_buildings(building_category=building_category, database_manager=database_manager)
area_forecast = buildings.build_area_forecast(database_manager)

demolition_floor_area = pd.Series(data=area_forecast.calc_total_demolition_area_per_year(), index=years)
yearly_constructed = ConstructionCalculator.calculate_construction(building_category, demolition_floor_area, database_manager)

constructed_floor_area = [v for v in yearly_constructed.accumulated_constructed_floor_area]
forecast = area_forecast.calc_area_with_construction(constructed_floor_area)

pp(forecast)


```
