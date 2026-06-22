
Getting started
===============
This page is a quick guide to get you started with the Energibruksmodell (EBM) model. The model is designed to calculate
energy use in the norwegian building stock. The model is developed by the
`Norwegian Water Resources and Energy Directorate (NVE) <https://www.nve.no>`_.


Requirements
------------

``EBM`` requires Python 3.11 or newer. Python is available from `python.org <https://www.python.org/downloads/>`_.

Additional requirements like pandas, pandera and openpyxl will be installed along side ``EBM``


Quick Start Guide
-----------------

Please, open your preferred terminal application and follow the instructions below.


Installation
^^^^^^^^^^^^

.. only:: internal

   .. admonition:: For NVE

      For kjøring internt hos NVE er ikke dette steget nødvendig. Du kan i stedet åpne
      ``Tilkobling mot eksternt skrivebord`` og bruke Datamaskin: |ebm_installation_host|. Dersom du ikke
      har tilgang til |ebm_installation_host|. Kontakt brukerstøtte.

      Når du er koblet til |ebm_installation_host| kan du gå videre til :ref:`What version of ebm are we running?`


Install ebm using pip


.. code-block:: bash

  python -m pip install ebm



What version of ebm are we running?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once installed, you need to setup input files with all the parameters required to  run ``EBM``. But before we do that, let's
check if ebm is working properly. Open a terminal (powershell) and type:

.. code-block:: bash

   ebm --version

The output should look something like this:

.. admonition:: expected output
   :collapsible: open
   :class: expected-output

   .. code-block:: powershell

    PS C:\Users\user> ebm --version
    ebm 0.99.2
    PS C:\Users\user>

The output shows what version of ebm you are running. Don't worry if the version number you get is a bit off from the one
in the example.


.. note::

    These instructions are made for |version|, but should work for later versions as well.

List available datasets
^^^^^^^^^^^^^^^^^^^^^^^^^

The following command lists all available input datasets:

.. code-block:: bash

   ebm list-input

.. admonition:: expected output
   :collapsible: closed
   :class: expected-output

   .. code-block:: powershell

      PS C:\Users\user\Documents> ebm list-input
      Available datasets: 
      - <dataset name 1>: <description of dataset 1> 

The output shows the names of the available datasets. If a dataset contains a ``README.md`` file with a ``Description``
section, the description will also be shown in the output. 

Create an input directory
^^^^^^^^^^^^^^^^^^^^^^^^^

Before running the model you need to create a directory with the necessary input files. The recommended way of creating
an input directory is to use ``create-input`` command.

``create-input`` is a command at the same level as ``list-input``:

.. code-block:: bash

   ebm list-input
   ebm create-input

The command can be used with or without arguments.

Create input from the default dataset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: bash

   ebm create-input

This creates an input directory basesd on the default dataset. 

Create input from a specific dataset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   ebm create-input tiks26

This creates an input directory based on the ``tiks26`` dataset.

Create input from a specific dataset with a custom directory name
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: bash

   ebm create-input tiks26 my-tiks26

This creates an input directory named ``my-tiks26`` based on the ``tiks26`` dataset. 


.. admonition:: expected output
   :collapsible: closed
   :class: expected-output

   .. code-block:: powershell

      PS C:\Users\user\Documents> ebm create-input tiks26 my-tiks26
      
      0:00:00.55 - Using data from "input"
      0:00:00.55- Copy input from C:\Users\user\pyc\Energibruksmodell\ebm\data\tiks26
      0:00:00.55 - Creating directory my-tiks26
      0:00:00.55 - Creating missing file  my-tiks26\building_code_parameters.csv
      0:00:00.55 - Creating missing file  my-tiks26\s_curve.csv
      0:00:00.55 - Creating missing file  my-tiks26\population_forecast.csv
      0:00:00.56- Creating missing file  my-tiks26\new_buildings_residential.csv
      0:00:00.56 - Creating missing file  my-tiks26\area_new_residential_buildings.csv
      0:00:00.57 - Creating missing file  my-tiks26\area.csv
      0:00:00.57 - Creating missing file  my-tiks26\energy_need_behaviour_factor.csv
      0:00:00.57 - Creating missing file  my-tiks26\energy_need_original_condition.csv
      0:00:00.57 - Creating missing file  my-tiks26\improvement_building_upgrade.csv
      0:00:00.57 - Creating missing file  my-tiks26\energy_need_improvements.csv
      0:00:00.57 - Creating missing file  my-tiks26\holiday_home_energy_consumption.csv
      0:00:00.58 - Creating missing file  my-tiks26\holiday_home_stock.csv
      0:00:00.58 - Creating missing file  my-tiks26\area_per_person.csv
      0:00:00.58 - Creating missing file  my-tiks26\heating_system_initial_shares.csv
      0:00:00.58 - Creating missing file  my-tiks26\heating_system_efficiencies.csv
      0:00:00.58 - Creating missing file  my-tiks26\heating_system_forecast.csv
      0:00:00.59 - Creating missing file  my-tiks26\README.md
      0:00:00.60 - Finished creating input files in my-tiks26


The command creates a new directory named ``input``, containing copies of all input files. By default, this directory is
created in the current working directory. To specify a different location, use the ``--input=<directory name>`` option.

If the directory already exists, only missing files will be copied. Existing files will not be overwritten.

If the dataset contains a ``README.md`` file, it is copied to the created input directory. This ensures that information
about the dataset is included together with the generated input files.

README.md descriptions
^^^^^^^^^^^^^^^^^^^^^^^^

Dataset descriptions shown by the ``ebm list-input`` are read from the dataset's ``README.md`` file. 

The description should be placed under a description heading in the ``README.md`` file, for example:

.. code-block:: markdown

   # Beskrivelse
   Short description of the dataset.

The text under this heading is read until the next heading and shown together with the dataset in ``ebm list-input``. 

List files in the input directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can use ``ls`` to get a list of all the files in the ``input`` directory:

.. code-block:: bash

    ls input


.. admonition:: expected output
   :collapsible: closed
   :class: expected-output

   .. code-block:: powershell

      PS C:\Users\user\Documents> ls input

           Directory: C:\Users\user\Documents\input
      
      Mode                 LastWriteTime         Length Name
      ----                 -------------         ------ ----
      -a----        30.09.2025     12:10           2475 area.csv
      -a----        30.09.2025     12:10            114 area_new_residential_buildings.csv
      -a----        30.09.2025     12:10            192 area_per_person.csv
      -a----        30.09.2025     12:10            238 building_code_parameters.csv
      -a----        30.09.2025     12:10            305 energy_need_behaviour_factor.csv
      -a----        30.09.2025     12:10            462 energy_need_improvements.csv
      -a----        30.09.2025     12:10          23191 energy_need_original_condition.csv
      -a----        30.09.2025     12:10           1340 heating_system_efficiencies.csv
      -a----        30.09.2025     12:10           1847 heating_system_forecast.csv
      -a----        30.09.2025     12:10          67093 heating_system_initial_shares.csv
      -a----        30.09.2025     12:10            446 holiday_home_energy_consumption.csv
      -a----        30.09.2025     12:10            652 holiday_home_stock.csv
      -a----        30.09.2025     12:10            475 improvement_building_upgrade.csv
      -a----        30.09.2025     12:10           1807 new_buildings_residential.csv
      -a----        30.09.2025     12:10            959 population_forecast.csv
      -a----        30.09.2025     12:10           1854 s_curve.csv


If your shell does not have the ``ls`` command, you might have better luck with ``dir``.


Run the model
^^^^^^^^^^^^^

You are now ready to run the model. Use the bare command ``EBM`` with no options:

.. code-block:: bash

   ebm


.. admonition:: expected output
   :collapsible: open
   :class: expected-output

   .. code-block:: powershell

      PS C:\Users\user\Documents> python -m ebm
      0:00:01.44 - Using data from "input"
      0:00:04.58 - Wrote output\area.xlsx
      0:00:04.97 - Wrote output\heating_system_share.xlsx
      0:00:05.34 - Wrote output\heat_prod_hp.xlsx
      0:00:09.32 - Wrote output\energy_use.xlsx
      0:00:17.10 - Wrote output\energy_purpose.xlsx
      0:00:18.39 - Wrote output\demolition_construction.xlsx


By default the scenario is read from ``input``, and the results are written to the subdirectory ``output`` in the
current working directory.

You can get a directory listing that shows all the result files created by issuing the command:

.. code-block:: bash

   ls output

The resulting output should look something like:

.. admonition:: expected output
   :collapsible: open
   :class: expected-output

   .. code-block:: powershell


           Directory: C:\Users\user\Documents\output


       Mode                 LastWriteTime         Length Name
       ----                 -------------         ------ ----
       -a----        18.09.2025     12:27          98844 area.xlsx
       -a----        18.09.2025     12:27         119998 demolition_construction.xlsx
       -a----        18.09.2025     12:27         647028 energy_purpose.xlsx
       -a----        18.09.2025     12:27         526083 energy_use.xlsx
       -a----        18.09.2025     12:27          32244 heating_system_share.xlsx
       -a----        18.09.2025     12:27           7349 heat_prod_hp.xlsx
       -a----        13.02.2025     11:18             50 README.md



The files can be opened using your favourite spreadsheet application. I.E. Microsoft Excel or LibreOffice Calc.


.. tip::

    If you want to open the results automatically as they become available, you can use the ``--open`` option.

    .. code-block:: bash

       ebm --open

.. seealso::

   :ref:`result files`
        An overview of the contents of all the output files.
   :ref:`Additional arguments <user-guide-additional-arguments>`
        Shows all the commands available for ``EBM``.
   :ref:`User case`
        gives a run-down on how you can change the input files to better suit your needs.


.. |date| date::

Last Updated on |date|.

Version: |version|.

