===============
Getting Started
===============


Installation
------------

To install the framework, run:

.. code-block:: bash

   pip install energibruksmodell


Quick Start Guide
-----------------

Here is a quick example of how to run your first model: test

.. code-block:: python

   import ebm

...


Running from the command line
-----------------------------
For å kjøre kommandoene under lokalt eller gjennom IDE er det nødvendig å starte som modul i stedet for program.

Eksempel:
    `ebm heating-systems`
blir til
    `python -m ebm heating-systems`


--------------------
Frivilige argumenter
--------------------

`ebm <--switch> <step> <output filename>`

Alle parametre listet over er frivilige. Standardvalg for `step` er `heating-systems` (endres muligens til energy-use). Standardvalg for `output filename` er `output/ebm_output.xlsx`

`ebm --help` gir en liste de fleste parametre.


----------
Kommandoer
----------

Help
^^^^

.. code:: bash

  python -m ebm --help

  usage: ebm [-h] [--version] [--debug] [--categories [CATEGORIES ...]] [--input [INPUT]] [--force] [--open] [--csv-delimiter CSV_DELIMITER] [--create-input] [--calibration-year [CALIBRATION_YEAR]] [--horizontal-years]
                          [{area-forecast,energy-requirements,heating-systems,energy-use}] [output_file]

  C  alculate EBM area forecast v0.17.2

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
    --open, -o            Open <filename> with default application after writing. (Usually Excel)
    --csv-delimiter CSV_DELIMITER, --delimiter CSV_DELIMITER, -e CSV_DELIMITER
                        A single character to be used for separating columns when writing csv. Default: "," Special characters like ; should be quoted ";"
    --create-input
                        Create input directory containing all required files in the current working directory
    --calibration-year [CALIBRATION_YEAR]
    --horizontal-years, --horizontal, --horisontal
                        Show years horizontal (left to right)


Beregne arealframskriving
^^^^^^^^^^^^^^^^^^^^^^^^^^
Hvor mye areal trenger oppvarming per år `=areal`

.. math::

  areal = areal startår - revet areal + bygget areal


.. code:: bash

  ebm area-forecast output/area-forecast-vertical.xlsx

.. code:: bash

  ebm --horizontal area-forecast output/area-forecast.xlsx


Beregne energibehov
^^^^^^^^^^^^^^^^^^^

Hva er oppvarmingsbehovet per kvadratmeter `=energibruk per m2 * areal`


.. math::

  redusert energibehov =  grunnbehov * adferdsfaktor * årligeffektivitetsfaktor * tilstandsfaktor

.. math::

  totalt energibehov = redusert energibehov * areal


.. code:: bash

  ebm energy-requirements output/energy-requirements-vertical.xlsx

.. code:: bash

  ebm --horizontal energy-requirements output/energy-requirements.xlsx


Energibruk
^^^^^^^^^^

Hvor mye energi er nødvendig per år `energibehov * effektivitetsgrad`

.. math::

  Energibruk = energibehov * effektivitetsgrad

.. code:: bash

  ebm --horizontal heating-systems output/heating-systems-vertical.xlsx

.. code:: bash

  ebm --horizontal heating-systems output/heating-systems.xlsx


Energibruk fritidsboliger
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: bash

  ebm --horizontal energy-use output/energy-use.xlsx` (holiday homes)


.. math::

  α_t(i) = P(O_1, O_2, … O_t, q_t = S_i λ)

