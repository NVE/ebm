.. |user_case_tek30| replace:: ``📁user-case-tek30``


Working with input
==================

EBM supports scenario-based modeling by allowing users to create and manage separate input directories. This enables
flexible experimentation with different assumptions and configurations.


List available datasets
-----------------------

The following command lists all available input datasets:

.. code-block:: bash

   ebm list-input

.. admonition:: expected output
   :collapsible: closed
   :class: expected-output

   .. code-block:: powershell

      PS C:\dev\ws\root> ebm list-input

      Available datasets:
      -------------------
      - long_analysis_2024: Standard input-datasett for LA25. Datasettet inneholder input-filer som
                            brukes for å kjøre ebm med forutsetninger for LA25. Datasettet er også
                            kalt prognosedatasettet fra høsten 2025.

      - original: Det originale ikke-kalibrerte datasettet.

      - short_analysis_2025: short_analysis_2025-datasettet inneholder oppdaterte forutsetninger
                             for framskriving av energibruk i bygg. De viktigste endringene gjelder
                             riving, innfasing av LED, virkningsgrader for oppvarmingsløsninger,
                             boligstørrelser, fordeling av nye boliger og kalibrering mot oppdatert
                             statistikk. Datasettet brukes som oppdatert grunnlag for framskriving av
                             energibruk i bygg i TIKS26. Datasettet gir et lavere utgangspunkt for
                             framskriving av kraftforbruk i bygg enn tidligere kalibrering,
                             samtidig som enkelte endringer, særlig knyttet til riving og
                             oppvarmingsløsninger, trekker energibruken opp isolert sett.


The output shows the names and a brief description of each dataset. The dataset names can be used to create new input directories for different scenarios.


Creating an input directory for a scenario
------------------------------------------

To create a new scenario in EBM, open your preferred terminal and run the following command:

.. code-block:: bash

   ebm create-input long_analysis_2024 --input=user-case-tek30


.. admonition:: expected output
   :collapsible: closed
   :class: expected-output

   .. code-block:: powershell

       Using data from "user-case-tek30"
       Copy input from C:\dev\ws\Energibruksmodell\ebm\data\long_analysis_2024
       Creating directory user-case-tek30
       Creating missing file  user-case-tek30\building_code_parameters.csv
       Creating missing file  user-case-tek30\s_curve.csv
       Creating missing file  user-case-tek30\population_forecast.csv
       Creating missing file  user-case-tek30\new_buildings_residential.csv
       Creating missing file  user-case-tek30\area_new_residential_buildings.csv
       Creating missing file  user-case-tek30\area.csv
       Creating missing file  user-case-tek30\energy_need_behaviour_factor.csv
       Creating missing file  user-case-tek30\energy_need_original_condition.csv
       Creating missing file  user-case-tek30\improvement_building_upgrade.csv
       Creating missing file  user-case-tek30\energy_need_improvements.csv
       Creating missing file  user-case-tek30\holiday_home_energy_consumption.csv
       Creating missing file  user-case-tek30\holiday_home_stock.csv
       Creating missing file  user-case-tek30\area_per_person.csv
       Creating missing file  user-case-tek30\heating_system_initial_shares.csv
       Creating missing file  user-case-tek30\heating_system_efficiencies.csv
       Creating missing file  user-case-tek30\heating_system_forecast.csv
       Creating missing file  user-case-tek30\building_category.csv
       Creating missing file  user-case-tek30\README.md
       Finished creating input files in user-case-tek30


The argument ``create-input`` will use the dataset ``long_analysis_2025`` as the basis for creating input files.
In this case the new input files will be copied to the subdirectory, |user_case_tek30|, as defined by the ``--input`` option.

If the directory you named does not exist, the program will attempt to create it.


.. tip::

    You can choose any valid directory name, but it is a good idea to limit to letters, numbers, and underscore. Avoid using space.


Using the input directory
-------------------------

Once the input directory is ready, you can run the model using:

.. code-block:: bash

   ebm --input=user-case-tek30

The model result calculated from the input files as defined in |user_case_tek30| will be written to the subdirectory |output_directory|.
|output_directory| will be created if it does not already exist.


The command above is an abbreviation of the command:

.. code-block:: bash

   ebm energy-use output/ --input=user-case-tek30

The arguments ``energy-use`` and ``output/`` are the defaults.


.. seealso::

   :ref:`Result files<result files>`

   :ref:`Additional Arguments<user-guide-additional-arguments>`


.. |date| date::

Last Updated on |date|

Version: |version|.
