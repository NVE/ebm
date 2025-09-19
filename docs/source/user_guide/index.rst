User Guide
==========

.. Basic Concepts
.. --------------
.. - Methods and calculations: :doc:`calculations`

.. - Models
.. - Parameters
.. - Workflows

.. Tutorials
.. ---------
..
.. - Running multiple workflows


.. toctree::
   :caption: Content
   :maxdepth: 1
   :hidden:

   getting_started
   user_case
   calibrating_the_model
   configuration
   troubleshooting
   geographical_distribution
   



Setting-up your first model (tutorial)
---------------------------------------

This is a step-by-step guide on how to set up your first model using the EBM model.

------------------------------------------------
1. How to run the program from the command line?
------------------------------------------------
For the commands to be excuted locally or in an IDE, it must be launched as a module rather than a program.

Example:

.. code-block:: python

    ebm heating-systems

should be excuted like:

.. code-block:: python

    python -m ebm heating-systems


.. _user-guide-additional-arguments:
--------------------
2. Additional arguments
--------------------
.. code-block:: python
    
    ebm <--switch> <step> <output filename>

The parameters listed above are optional. The default choice for the ``step`` parameter is ``energy-use``, and the default output filename is ``output/ebm_output.xlsx``.


.. csv-table:: Difference between switch and step
  :file: ..\tables\diff_switch_step.csv
  :widths: 3, 20
  :header-rows: 1

.. `ebm --help` gir en liste de fleste parametre.


------------------------------------------------------
3. Example of how to run your first model: test
------------------------------------------------------

Help command
^^^^^^^^^^^^
Typing `ebm --help` will give you a list of most parameters:


.. code:: bash

  ebm --help

  usage: ebm [-h] [--version] [--debug] [--categories [CATEGORIES ...]] [--input [INPUT]] [--force] [--open] [--csv-delimiter CSV_DELIMITER] [--create-input] [--horizontal-years] [{area-forecast,energy-requirements,heating-systems,energy-use}] [output_file]

Calculate EBM energy use 1.1.10

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
  --horizontal-years, --horizontal, --horisontal
                        Show years horizontal (left to right)


.. ----------
.. Kommandoer
.. ----------

.. Calculate area projection
4. Calculate the projected annual area requiring heating
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. 
  Hvor mye areal trenger oppvarming per år `=areal`

.. .. .. math::

..   
  areal = areal startår - revet areal + bygget areal


.. code:: bash

  # This is the default cammand, where the output file is area-forecast-vertical.xlsx located 
  # in the output directory
  # The output file will be written in vertical format
  ebm area-forecast output/area-forecast-vertical.xlsx
  
.. csv-table:: Output from using the command above
  :file: ..\tables\example_four_output.csv
  :header-rows: 1
  

If the user wants the output file in horizontal format, the user can use the following command:

.. code:: bash

  # This command will write the output file in horizontal format with the name area-forecast.xlsx
  ebm --horizontal area-forecast output/area-forecast.xlsx

.. csv-table:: Output from using the command above (horizontal format)
  :file: ..\tables\example_four_output_horizontal.csv
  :header-rows: 1

.. Beregne energibehov

5. Calculate energy-requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The energy-requirements is calculated by multiplying the heating demand per square meter by the area from the previous step.

.. Hva er oppvarmingsbehovet per kvadratmeter `=energibruk per m2 \times areal`


.. .. math::

..   redusert energibehov =  grunnbehov \times adferdsfaktor \times årligeffektivitetsfaktor \times tilstandsfaktor

.. .. math::

..   totalt energibehov = redusert energibehov \times areal


.. code:: bash

  # This is the default cammand, where the output file is energy-requirements-vertical.xlsx located
  # in the output directory
  ebm energy-requirements output/energy-requirements-vertical.xlsx

.. csv-table:: Output from using the command above 
  :file: ..\tables\example_five_output.csv
  :header-rows: 1

If the user wants the output file in horizontal format, the user can use the following command:

.. code:: bash

  # This command will write the output file in horizontal format with the name energy-requirements.xlsx
  ebm --horizontal energy-requirements output/energy-requirements.xlsx

.. csv-table:: Output from using the command above (horizontal format)
  :file: ..\tables\example_five_output_horizontal.csv
  :header-rows: 1


6. Energy consumption
^^^^^^^^^^^^^^^^^^^^^

The energy consumption is calculated by multiplying the energy requirements from the previous step by the efficiency factor.

.. Hvor mye energi er nødvendig per år `energibehov * effektivitetsgrad`

.. .. math::

..   Energibruk = energibehov * effektivitetsgrad


.. code:: bash

  # This is the default command, where the output file is heating-systems-vertical.xlsx located
  # in the output directory
  ebm heating-systems output/heating-systems-vertical.xlsx

.. csv-table:: Output from using the command above 
  :file: ..\tables\example_six_output.csv
  :header-rows: 1

.. If the user wants the output file in horizontal format, the user can use the following command:

.. .. code:: bash

..   # This command will write the output file in horizontal format with the name heating-systems.xlsx
..   ebm --horizontal heating-systems output/heating-systems.xlsx


.. Energibruk fritidsboliger

7. Holiday homes energy consumption
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: bash

  # This is the default command, where the output file is energy-use-vertical.xlsx located
  # in the output directory
  ebm energy-use output/energy-use-vertical.xlsx

.. csv-table:: Output from using the command above
  :file: ..\tables\example_seven_output.csv
  :header-rows: 1

.. # This command will write the output file in horizontal format with the name energy-use.xlsx
.. ebm --horizontal energy-use output/energy-use.xlsx


.. .. math::

  .. α_t(i) = P(O_1, O_2, … O_t, q_t = S_i λ)


8. Example case
^^^^^^^^^^^^^^^

If the user wants to run the program with input files located in another directory, for instance the "calibration" directory, the user can use the following command:

.. code:: bash
  
  # This command will run the program with input files located in the "calibration" directory
  ebm --input calibration energy-use output/energy-use.xlsx

.. |date| date::

Last Updated on |date|.

Version: |version|.
