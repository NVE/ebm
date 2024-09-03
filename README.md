# Introduction 
TODO: Give a short introduction of your project. Let this section explain the objectives or the motivation behind this project. 

# Getting Started
TODO: Guide users through getting your code up and running on their own system. In this section you can talk about:

## More information
 - [Detailed developer documentation found here (Norwegian)](docs/README.md)
 - [How to build the project](docs/BUILD.md)


## 1. Installation process
Open a terminal application and navigate to wherever you want to do work. 

### Make a python virtual environment (optional)
While optional, it is always recommended to install and run python modules in a discrete virtual environment. To create a 
new python virtual environment (venv) type the following in a terminal.

 `python -m venv venv`

## Activate virtual environment
To use your venv you need to activate it
### Using powershell
(Your command prompt starts with PS) 
`\venv\Scripts\active.ps1`

### Using cmd
(Your command prompt starts with C:\ where C is any letter from A-Z)
`\venv\Scripts\active.bat`

###
`python -m pip install pandas openpyxl loguru python-dotenv rich`

### Download energibruksmodell module from here
  https://pkgs.dev.azure.com/NVE-devops/Energibruksmodell/_apis/packaging/feeds/a3118afb-b44a-4e53-83af-0d4657833457/pypi/packages/energibruksmodell/versions/0.7.6/energibruksmodell-0.7.6-py3-none-any.whl/content

### Install Energibruksmodell
`python -m pip install energibruksmodell-0.7.6-py3-none-any.whl`

### Run Energibruksmodell
 Refer to section [Running as a script](#running-as-a-script) below

    
    
## 2. Software dependencies
  - pandas
  - loguru
  - rich
  - openpyxl
   
  See also [requirements.txt](requirements.txt)

## 3. Run

### Running as a script

There are multiple ways to run the program. Listed bellow is running as a standalone program and running as a module. If 
running as a program fails due to security restriction, you might be able to use the module approach instead. See also [Running as code](#running-as-code)

```cmd
calculate-area-forecast
```

### Running as a module

```cmd
python3 -m ebm
```

For more information use `--help`

`python -m ebm --help`

```shell
python -m ebm --help

usage: calculate-area-forecast [-h] [--version] [--debug] [--force] [--open] [--csv-delimiter CSV_DELIMITER] [--create-input] [--start_year [START_YEAR]] [--end_year [END_YEAR]] [--horizontal]
                               [output_file] [building_categories ...]

Calculate EBM area forecast v0.7.9

positional arguments:
  output_file           The location of the file you want to be written. default: output\ebm_area_forecast.xlsx
                            If the file already exists the program will terminate without overwriting.
                            Use "-" to output to the console instead
  building_categories
                        One or more of the following building categories:
                            house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs

options:
  -h, --help            show this help message and exit
  --version, -v         show program's version number and exit
  --debug, -d           Run in debug mode. (Extra information written to stdout)
  --force, -f           Write to <filename> even if it already exists
  --open, -o            Attempt opening <filename> after writing
  --csv-delimiter CSV_DELIMITER, --delimiter CSV_DELIMITER, -e CSV_DELIMITER
                        A single character to be used for separating columns when writing csv. Default: "," Special characters like ; should be quoted ";"
  --create-input        Create input directory with all required files in the current working directory
  --start_year [START_YEAR]
                        Forecast start year. default: 2010, all other values are invalid
  --end_year [END_YEAR]
                        Forecast end year (including). default: 2050, any other values are invalid
  --horizontal          Show years horizontal (left to right)
```


### Running as code
```python

from ebm.model import BuildingCategory, Buildings, DatabaseManager
from ebm.model.construction import ConstructionCalculator

database_manager = DatabaseManager()

buildings = Buildings.build_buildings(building_category=BuildingCategory.HOUSE)

area_forecast = buildings.build_area_forecast(database_manager)

demolished_floor_area = area_forecast.calc_total_demolition_area_per_year()

yearly_constructed = ConstructionCalculator.calculate_construction_as_list(
    building_category=BuildingCategory.HOUSE,
    demolition_floor_area=demolished_floor_area)

forecast = area_forecast.calc_area_with_construction(yearly_constructed)

print(forecast)


```
