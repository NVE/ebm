===============
Getting started
===============
This page is a quick guide to get you started with the Energibruksmodell (EBM) framework. The framework is designed to calculate energy use in buildings. The framework is developed by the Norwegian Water Resources and Energy Directorate (NVE).

Installation
------------

To install the framework, run:

.. code-block:: python
  
  python -m pip install energibruksmodell


Quick Start Guide
-----------------
To know which EBM version you have installed, type:

.. code-block:: python

   ebm --version

First of all, you need to create a directory with the necessary input files. To do this, run:

.. code-block:: python

  ebm --create-input




.. Here is a quick example of how to run your first model: test

.. .. code-block:: python

..    import ebm

.. ...


.. Running from the command line
.. -----------------------------
.. For the commands to be excuted locally or in an IDE, it must be launched as a module rather than a program.

.. Example:
..     `ebm heating-systems`
.. should be excuted like:
..     `python -m ebm heating-systems`


.. --------------------
.. Additional arguments
.. --------------------

.. `ebm <--switch> <step> <output filename>`

.. The parameters listed above are optional. The default choice for the `step` parameter is `energy-use`, and the default output filename is `output/ebm_output.xlsx`.
.. `ebm --help` gir en liste de fleste parametre.


.. ------------------------------------------------------
.. The following are different commands that can be used
.. ------------------------------------------------------

.. Help
.. ^^^^

.. .. code:: bash

..   ebm --help

..   usage: ebm [-h] [--version] [--debug] [--categories [CATEGORIES ...]] [--input [INPUT]] [--force] [--open] [--csv-delimiter CSV_DELIMITER]
..            [--create-input] [--horizontal-years][{area-forecast,energy-requirements,heating-systems,energy-use}] [output_file]

..   Calculate EBM energy use 1.0.0

..   positional arguments:
..     {area-forecast,energy-requirements,heating-systems,energy-use}

..                         The calculation step you want to run. The steps are sequential. Any prerequisite to the chosen step will run
..                             automatically.
..   output_file           The location of the file you want to be written. default: output\ebm_output.xlsx
..                             If the file already exists the program will terminate without overwriting.
..                             Use "-" to output to the console instead

..   options:
..     -h, --help            show this help message and exit
..     --version, -v         show program's version number and exit
..     --debug               Run in debug mode. (Extra information written to stdout)
..     --categories [CATEGORIES ...], --building-categories [CATEGORIES ...], -c [CATEGORIES ...]

..                           One or more of the following building categories:
..                               house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs.
..                               The default is to use all categories.
..     --input [INPUT], --input-directory [INPUT], -i [INPUT]
..                         path to the directory with input files
..     --force, -f           Write to <filename> even if it already exists
..     --open, -o            Open <filename> with default application after writing. (Usually Excel)
..     --csv-delimiter CSV_DELIMITER, --delimiter CSV_DELIMITER, -e CSV_DELIMITER
..                         A single character to be used for separating columns when writing csv. Default: "," Special characters like ; should be quoted ";"
..     --create-input      Create input directory containing all required files in the current working directory
..     --calibration-year [CALIBRATION_YEAR]
..     --horizontal-years, --horizontal, --horisontal
..                         Show years horizontal (left to right)


.. .. ----------
.. .. Kommandoer
.. .. ----------

.. .. Calculate area projection
.. Calculate the projected annual area requiring heating
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. .. 
..   Hvor mye areal trenger oppvarming per år `=areal`

.. .. .. .. math::

.. ..   
..   areal = areal startår - revet areal + bygget areal


.. .. code:: bash

..   # This is the default cammand, where the output file is area-forecast-vertical.xlsx located 
..   # in the output directory
..   # The output file will be written in vertical format
..   ebm area-forecast output/area-forecast-vertical.xlsx
  
  
..   # This command will write the output file in horizontal format with the name area-forecast.xlsx
..   ebm --horizontal area-forecast output/area-forecast.xlsx


.. .. Beregne energibehov
.. Calculate energy-requirements
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. The energy-requirements is calculated by multiplying the heating demand per square meter by the area.

.. .. Hva er oppvarmingsbehovet per kvadratmeter `=energibruk per m2 * areal`


.. .. .. math::

.. ..   redusert energibehov =  grunnbehov * adferdsfaktor * årligeffektivitetsfaktor * tilstandsfaktor

.. .. .. math::

.. ..   totalt energibehov = redusert energibehov * areal


.. .. code:: bash

..   # This is the default cammand, where the output file is energy-requirements-vertical.xlsx located
..   # in the output directory
..   ebm energy-requirements output/energy-requirements-vertical.xlsx


..   # This command will write the output file in horizontal format with the name energy-requirements.xlsx
..   ebm --horizontal energy-requirements output/energy-requirements.xlsx


.. Energy consumption
.. ^^^^^^^^^^^^^^^^^^^	

.. The energy consumption is calculated by multiplying the energy requirements by the efficiency factor.

.. .. Hvor mye energi er nødvendig per år `energibehov * effektivitetsgrad`

.. .. .. math::

.. ..   Energibruk = energibehov * effektivitetsgrad


.. .. code:: bash

..   # This is the default cammand, where the output file is energy-use-vertical.xlsx located
..   # in the output directory
..   ebm --horizontal heating-systems output/heating-systems-vertical.xlsx

..   # This command will write the output file in horizontal format with the name heating-systems.xlsx
..   ebm --horizontal heating-systems output/heating-systems.xlsx


.. .. Energibruk fritidsboliger
.. Holiday homes energy consumption
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. .. code:: bash

..   # This is the default cammand, where the output file is energy-use-vertical.xlsx located
..   # in the output directory
..   ebm --horizontal energy-use output/energy-use.xlsx` 


.. .. .. math::

..   .. α_t(i) = P(O_1, O_2, … O_t, q_t = S_i λ)

