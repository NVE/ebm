#  Introduction 

EBM is a model used by the Norwegian Water Resources and Energy Directorates (NVE) to forecast energy use in the 
building stock. EBM is an open-source model developed and managed by NVE. The model allows the user to analyze how 
demographic trends and policy instruments impact the yearly energy use on a national and regional level. Energy use is 
estimated by a bottom- up approach, based on the building stock floor area, energy need and distribution of heating 
systems. The mathematical model is implemented in Python, with input and output files in excel or csv.


![ebm-in-windows-terminal.png](docs/source/_static/getting_started/ebm-in-windows-terminal.png)


# Getting Started

## More information


 - [Full documentation found here](https://nve.github.io/ebm-docs/index.html)
   - [Model description](https://nve.github.io/ebm-docs/model_description/index.html)
   - [Limitations](https://nve.github.io/ebm-docs/limitations.html)
   - [Getting started](https://nve.github.io/ebm-docs/user_guide/getting_started.html)
   - [Troubleshooting](https://nve.github.io/ebm-docs/user_guide/troubleshooting.html)


## 1. Installation process

Please refer to [getting started](https://nve.github.io/ebm-docs/user_guide/getting_started.html) for information on 
how ti install EBM as a user. 

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

### GNU/Linux and macOS

`source venv/bin/active`

More information on [Python virtual environments](https://realpython.com/python-virtual-environments-a-primer/)


## Install EBM

There are two options. **Install from PyPI** (Python package index) or install **clone the github repository**.

### Install from PyPI

`python -m pip install ebm`

You can now run the model as a module `python -m ebm` or as a program `ebm`

Please refer to [getting started](https://nve.github.io/ebm-docs/user_guide/getting_started.html) for more information on how the model works.


### Clone the github repository

`git clone https://github.com/NVE/ebm`

`cd ebm`

Make sure your current working directory is the EBM root. 

```
python -m pip install -e .

```

The command will install install all dependencies and ebm as an editable module.

    
    
## 2. Software dependencies
  - pandas
  - loguru
  - openpyxl
  - pandera
   
  Dependecies will be automatically installed when you install the package as described under Installation process.
  See also [requirements.txt](requirements.txt)

## 3. Run the model

There are multiple ways to run the program. Listed bellow is running as a standalone program and running as a module. If 
running as a program fails due to security restriction, you might be able to use the module approach instead. 

See also [Running as code](#running-as-code)


### Running as a module

```cmd
python3 -m ebm
```

By default, the results will be written to the subdirectory `output`

For more information use `--help`

`python -m ebm --help`

```shell
usage: ebm [-h] [--version] [--debug] [--categories [CATEGORIES ...]] [--input [INPUT]] [--force] [--open]
           [--csv-delimiter CSV_DELIMITER] [--create-input] [--horizontal-years]
           [{area-forecast,energy-requirements,heating-systems,energy-use}] [output_file]

Calculate EBM energy use 1.2.15

positional arguments:
  {area-forecast,energy-requirements,heating-systems,energy-use}

                        The calculation step you want to run. The steps are sequential. Any prerequisite to the chosen step will run
                            automatically.
  output_file           The location of the file you want to be written. default: output\ebm_output.xlsx
                            If the file already exists the program will terminate without overwriting.
                            Use "-" to output to the console instead

options:
  -h, --help            show this help message and exit
  --version, -v         show program's version number and exit
  --debug               Run in debug mode. (Extra information written to stdout)
  --categories [CATEGORIES ...], --building-categories [CATEGORIES ...], -c [CATEGORIES ...]

                        One or more of the following building categories:
                            house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs.
                            The default is to use all categories.
  --input [INPUT], --input-directory [INPUT], -i [INPUT]
                        path to the directory with input files
  --force, -f           Write to <filename> even if it already exists
  --open, -o            Open output file(s) automatically when finished writing. (Usually Excel)
  --csv-delimiter CSV_DELIMITER, --delimiter CSV_DELIMITER, -e CSV_DELIMITER
                        A single character to be used for separating columns when writing csv. Default: "," Special characters like ; should be quoted ";"
  --create-input
                        Create input directory containing all required files in the current working directory
  --horizontal-years, --horizontal, --horisontal
                        Show years horizontal (left to right)
```


### Running as code
```python

from ebm.temp_calc import calculate_energy_use_wide
from ebm.model.file_handler import FileHandler

fh = FileHandler()
fh.create_missing_input_files()

df = calculate_energy_use_wide(ebm_input=fh.input_directory)
print(df)

```

## License
This project is licensed under the MIT License. You are free to use, modify, and distribute the software with proper attribution.

## Contributing
We welcome contributions! Please refer to the Contributing Guide (CONTRIBUTING.md) for details on how to get started.

## Documentation
Full documentation is available at the EBM User Guide: https://nve.github.io/ebm/



