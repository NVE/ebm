
Getting started
===============
This page is a quick guide to get you started with the Energibruksmodell (EBM) model. The model is designed to calculate
energy use in the norwegian building stock. The model is developed by the
`Norwegian Water Resources and Energy Directorate (NVE) <https://www.nve.no>`_.


Requirements
------------

``EBM`` requires Python 3.11 or newer.


Quick Start Guide
-----------------

Please, open your preferred terminal and follow the instructions below.

.. image:: ../_static/getting_started/ebm-in-windows-terminal.png


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

  python -m pip install energibruksmodell




.. note::

    To figure out what EBM version you have installed, you can type ``ebm --version``
    These instructions are made for |version|, but should work for later versions as well.


What version of ebm are we running?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once installed need to setup input files with all the parameters required to  run ``EBM``. But before we do that, let's
check if ebm is working properly. Open a terminal (powershell) and type:

.. code-block:: bash

   ebm --version

The output should look something like this:

.. admonition:: expected output
   :collapsible: open
   :class: expected-output

   .. code-block:: powershell

    PS C:\Users\user> ebm --version
    ebm 1.2.9
    PS C:\Users\user>

The output show what version of ebm you are running. Don't worry if the version number you get is a bit off from the one
in the example. It will probably be fine.


Create an input directory
^^^^^^^^^^^^^^^^^^^^^^^^^

Before running the model you need to create a directory with the necessary input files. The recommended way of creating
the directory is to use ebm:

.. code-block:: bash

   ebm --create-input


.. admonition:: expected output
   :collapsible: closed
   :class: expected-output

   .. code-block:: powershell

      PS C:\Users\user\Documents> python -m ebm --create-input
      0:00:01.25 - Using data from "input"
      0:00:01.26 - Copy input from C:\Users\user\pyc\Energibruksmodell\ebm\data
      0:00:01.26 - Creating directory input
      0:00:01.28 - Creating missing file  input\building_code_parameters.csv
      0:00:01.30 - Creating missing file  input\s_curve.csv
      0:00:01.33 - Creating missing file  input\population_forecast.csv
      0:00:01.35 - Creating missing file  input\new_buildings_residential.csv
      0:00:01.38 - Creating missing file  input\area_new_residential_buildings.csv
      0:00:01.42 - Creating missing file  input\area.csv
      0:00:01.45 - Creating missing file  input\energy_need_behaviour_factor.csv
      0:00:01.48 - Creating missing file  input\energy_need_original_condition.csv
      0:00:01.51 - Creating missing file  input\improvement_building_upgrade.csv
      0:00:01.54 - Creating missing file  input\energy_need_improvements.csv
      0:00:01.57 - Creating missing file  input\holiday_home_energy_consumption.csv
      0:00:01.60 - Creating missing file  input\holiday_home_stock.csv
      0:00:01.62 - Creating missing file  input\area_per_person.csv
      0:00:01.65 - Creating missing file  input\heating_system_initial_shares.csv
      0:00:01.68 - Creating missing file  input\heating_system_efficiencies.csv
      0:00:01.71 - Creating missing file  input\heating_system_forecast.csv
      0:00:01.71 - Finished creating input files in input


The command creates a new directory called ``input`` with the default input parameters. You can use a different directory
by adding the ``--input=<directory name>`` option.


Run the model
^^^^^^^^^^^^^

You are now ready to run the model. Use the bare command ``ebm`` with no options:

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


By default the scenario is read from ``input``, and the results are written to the directory ``output``.

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


If your shell does not have the ``ls`` command, you might have better luck with ``dir``.

The files can be opened using your favourite spreadsheet application. I.E. Microsoft Excel or LibreOffice Calc.



.. tip::

    If you want to open the results automatically as they become available, you can use the switch ``--open``.

    .. code-block:: bash

       ebm --open



.. seealso::

   :ref:`result files`
        An overview of the contents of all the output files.
   :ref:`Additional arguments <user-guide-additional-arguments>`
        Shows all the commands available for ``ebm``.
   :ref:`User case`
        gives a run-down on how you can change the input files to better suit your needs.



.. |date| date::

Last Updated on |date|.

Version: |version|.

