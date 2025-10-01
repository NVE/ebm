User case
=========


This guide demonstrates how to create and configure a new scenario in EBM by introducing a hypothetical future building code: *TEK30*.
Scenario-based modeling in EBM allows users to explore alternative planning assumptions, regulatory changes, and energy performance impacts by managing separate input directories.

The TEK30 scenario showcases how to:
 - Create a dedicated input directory for scenario data
 - Define a new building code and its timeline
 - Specify energy needs across building categories
 - Configure heating system shares
 - Optionally adjust lighting improvements


Working with input
------------------

EBM supports scenario-based modeling by allowing users to create and manage separate input directories. This enables
flexible experimentation with different assumptions and configurations.


Creating an input directory for a scenario
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To create a new scenario in EBM, open your preferred terminal and run the following command:

.. code-block:: bash

   ebm --create-input --input=user-case-tek30


The input directory will be created using the path defined by the `--input` switch. In this case the new input files will be
created in the subdirectory `user-case-tek30`.

If the directory you name does not exist, the program will attempt to create it. All input files necessary to run ebm
will be created, with their default values, in the supplied path.


.. tip::

    You can choose any valid directory name, but it is a good idea to limit to letters, numbers, and underscore. Avoid using space.


Using the input directory
^^^^^^^^^^^^^^^^^^^^^^^^^

Once the input directory is ready, you can run the model using:

.. code-block:: bash

   ebm --input=user-case-tek30

The model result as defined in with user-case-tek30 will be written to the subdirectory ``output``.

.. seealso::

   :ref:`Results <results>`


User case: Add a new building code
----------------------------------

This example demonstrates how to use EBM’s scenario functionality by adding a new building code. TEK30 represents
a hypothetical future building code introduced as part of a user case to demonstrate how EBM handles scenario-based
modeling.


To add TEK30 to ebm you have to edit a number of files in the subdirectory ``user-case-tek30``
 - :ref:`Add the new building code to the model in building_code_parameters.csv<add the new building code>`
 - :ref:`Define energy needs for TEK30 in energy_need_original_condition.csv<define energy needs for TEK30>`
 - :ref:`Specify heating system shares in heating_system_initial_shares.csv<Specify heating system shares>`


This process showcases how EBM can be extended to simulate future regulations or alternative planning assumptions.


Add the new building code
^^^^^^^^^^^^^^^^^^^^^^^^^

The timeline and classification of building codes used by EBM are defined in the csv file ``building_code_parameters.csv``.
To include TEK30 in your scenario, you must first define it in that file.

You can edit building_code_parameters.csv using a
plain text editor (e.g., Notepad) or spreadsheet software such as Microsoft Excel or LibreOffice Calc.


.. tip::

   When using spreadsheet software, ensure the correct formatting is preserved when saving as CSV.
    - Use comma ``,`` as the delimiter
    - Use full stop ``.`` as the decimal separator


.. Set the following values in building_code_parameters.csv:
     - building_code: TEK30
     - building_year: 2040
     - period_start_year: 2030
     - period_end_year: 2050



Add the following line to ``user-case-tek30/building_code_parameters.csv`` to define TEK30 as a new building code entry:

.. code-block:: text

   TEK30,2040,2030,2050

The comma-separated columns in the line you added represent the following: building code, building year (in relation to S-curves),
start year for the building code, and end year for the building code. Both the start and end years are inclusive.


.. seealso::

   Other -> building_code under :ref:`input constraints`


EBM does not allow overlapping periods in building_code_parameters.csv. Since TEK17 currently ends in 2050, we must adjust the end year for TEK17 as well:

 To avoid overlapping periods, update the TEK17 entry in ``building_code_parameters.csv`` as follows:

.. code-block:: text

   TEK17,2025,2020,2029


When done correctly ``building_code_parameters.csv`` should look like the example below.

.. tabs::

   .. tab:: Formatted table

        Below is the updated content of building_code_parameters.csv. The new TEK30 entry and the adjusted end period for TEK17 are outlined in bold.

        .. csv-table:: Complete building_code_parameters.csv
           :header: "building_code", "building_year", "period_start_year", "period_end_year"
           :widths: 11, 6, 6, 6

           PRE_TEK49, 1945, 0, 1948
           TEK49,1962,1949,1968
           TEK  69,1977,1969,1986
           TEK87,1991,1987,1996
           TEK97,2002,1997,2006
           TEK07,2012,2007,2010
           TEK10,2018,2011,2019
           TEK17,2025,2020,**2029**
           **TEK30**,**2040**,**2030**,**2050**

   .. tab:: Raw CSV

        You can add the raw excel content at the end of building_code_parameters.csv using notepad or a similar text editor.

        .. code-block:: csv

            building_code,building_year,period_start_year,period_end_year
            PRE_TEK49,1945,0,1948
            TEK49,1962,1949,1968
            TEK69,1977,1969,1986
            TEK87,1991,1987,1996
            TEK97,2002,1997,2006
            TEK07,2012,2007,2010
            TEK10,2018,2011,2019
            TEK17,2025,2020,2029
            TEK30,2040,2030,2050

   .. tab:: Download

        Optionally, `Download building_code_parameters.csv <_static/user_case/tek30/building_code_parameters.csv>`_ working example.

Define energy need for TEK30
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All building codes must have it's energy need defined in :ref:`energy_need_original_condition.csv<energy_need_original_condition>`. For this scenario we assume a TEK30 have a 2/3 energy need reduction for heating_rv and 1/4 reduction for heating_dhw, cooling, fans_and_pumps and electrical_equipment.

.. tabs::

   .. tab:: Summary table

        Open *formatted table* and *raw csv* for complete listings

        .. csv-table:: Summary energy_need_original_condition.csv
           :header: building_category,building_code,purpose,kwh_m2

               house,TEK30,heating_rv,15.83
               house,TEK30,heating_dhw,16.76
               house,TEK30,fans_and_pumps,3.61
               house,TEK30,electrical_equipment,9.86
               house,TEK30,cooling,0.0
               …,…,…,…
               storage_repairs,TEK30,heating_rv,25.27
               storage_repairs,TEK30,heating_dhw,5.64
               storage_repairs,TEK30,fans_and_pumps,8.5
               storage_repairs,TEK30,electrical_equipment,13.22
               storage_repairs,TEK30,cooling,8.16


   .. tab:: Formatted table

        You should be able to paste the content of this table into energy_need_original_condition.csv when using Excel

        .. csv-table:: Excerpt energy_need_original_condition.csv
           :header: building_category,building_code,purpose,kwh_m2

               house,TEK30,heating_rv,15.83
               house,TEK30,heating_dhw,16.76
               house,TEK30,fans_and_pumps,3.61
               house,TEK30,electrical_equipment,9.86
               house,TEK30,cooling,0.0
               apartment_block,TEK30,heating_rv,9.61
               apartment_block,TEK30,heating_dhw,16.75
               apartment_block,TEK30,fans_and_pumps,4.26
               apartment_block,TEK30,electrical_equipment,9.86
               apartment_block,TEK30,cooling,0.0
               retail,TEK30,heating_rv,16.56
               retail,TEK30,heating_dhw,5.9
               retail,TEK30,fans_and_pumps,22.38
               retail,TEK30,electrical_equipment,2.1
               retail,TEK30,cooling,16.82
               office,TEK30,heating_rv,8.63
               office,TEK30,heating_dhw,2.82
               office,TEK30,fans_and_pumps,9.14
               office,TEK30,electrical_equipment,19.38
               office,TEK30,cooling,8.68
               kindergarten,TEK30,heating_rv,24.74
               kindergarten,TEK30,heating_dhw,5.64
               kindergarten,TEK30,fans_and_pumps,12.64
               kindergarten,TEK30,electrical_equipment,2.94
               kindergarten,TEK30,cooling,0.0
               school,TEK30,heating_rv,15.34
               school,TEK30,heating_dhw,5.51
               school,TEK30,fans_and_pumps,13.45
               school,TEK30,electrical_equipment,7.26
               school,TEK30,cooling,0.0
               university,TEK30,heating_rv,8.53
               university,TEK30,heating_dhw,2.82
               university,TEK30,fans_and_pumps,10.96
               university,TEK30,electrical_equipment,19.38
               university,TEK30,cooling,10.82
               hospital,TEK30,heating_rv,26.01
               hospital,TEK30,heating_dhw,16.75
               hospital,TEK30,fans_and_pumps,24.4
               hospital,TEK30,electrical_equipment,26.28
               hospital,TEK30,cooling,17.31
               nursing_home,TEK30,heating_rv,30.01
               nursing_home,TEK30,heating_dhw,16.76
               nursing_home,TEK30,fans_and_pumps,27.26
               nursing_home,TEK30,electrical_equipment,13.14
               nursing_home,TEK30,cooling,0.0
               hotel,TEK30,heating_rv,16.94
               hotel,TEK30,heating_dhw,16.76
               hotel,TEK30,fans_and_pumps,15.96
               hotel,TEK30,electrical_equipment,3.28
               hotel,TEK30,cooling,11.77
               sports,TEK30,heating_rv,18.26
               sports,TEK30,heating_dhw,27.57
               sports,TEK30,fans_and_pumps,9.92
               sports,TEK30,electrical_equipment,1.46
               sports,TEK30,cooling,0.0
               culture,TEK30,heating_rv,19.5
               culture,TEK30,heating_dhw,5.64
               culture,TEK30,fans_and_pumps,11.42
               culture,TEK30,electrical_equipment,1.61
               culture,TEK30,cooling,8.96
               storage_repairs,TEK30,heating_rv,25.27
               storage_repairs,TEK30,heating_dhw,5.64
               storage_repairs,TEK30,fans_and_pumps,8.5
               storage_repairs,TEK30,electrical_equipment,13.22
               storage_repairs,TEK30,cooling,8.16


   .. tab:: Raw csv

        You can add the raw excel content at the end of energy_need_original_condition.csv using notepad or a similar text editor.

        .. code-block:: text

               house,TEK30,heating_rv,15.83
               house,TEK30,heating_dhw,16.76
               house,TEK30,fans_and_pumps,3.61
               house,TEK30,electrical_equipment,9.86
               house,TEK30,cooling,0.0
               apartment_block,TEK30,heating_rv,9.61
               apartment_block,TEK30,heating_dhw,16.75
               apartment_block,TEK30,fans_and_pumps,4.26
               apartment_block,TEK30,electrical_equipment,9.86
               apartment_block,TEK30,cooling,0.0
               retail,TEK30,heating_rv,16.56
               retail,TEK30,heating_dhw,5.9
               retail,TEK30,fans_and_pumps,22.38
               retail,TEK30,electrical_equipment,2.1
               retail,TEK30,cooling,16.82
               office,TEK30,heating_rv,8.63
               office,TEK30,heating_dhw,2.82
               office,TEK30,fans_and_pumps,9.14
               office,TEK30,electrical_equipment,19.38
               office,TEK30,cooling,8.68
               kindergarten,TEK30,heating_rv,24.74
               kindergarten,TEK30,heating_dhw,5.64
               kindergarten,TEK30,fans_and_pumps,12.64
               kindergarten,TEK30,electrical_equipment,2.94
               kindergarten,TEK30,cooling,0.0
               school,TEK30,heating_rv,15.34
               school,TEK30,heating_dhw,5.51
               school,TEK30,fans_and_pumps,13.45
               school,TEK30,electrical_equipment,7.26
               school,TEK30,cooling,0.0
               university,TEK30,heating_rv,8.53
               university,TEK30,heating_dhw,2.82
               university,TEK30,fans_and_pumps,10.96
               university,TEK30,electrical_equipment,19.38
               university,TEK30,cooling,10.82
               hospital,TEK30,heating_rv,26.01
               hospital,TEK30,heating_dhw,16.75
               hospital,TEK30,fans_and_pumps,24.4
               hospital,TEK30,electrical_equipment,26.28
               hospital,TEK30,cooling,17.31
               nursing_home,TEK30,heating_rv,30.01
               nursing_home,TEK30,heating_dhw,16.76
               nursing_home,TEK30,fans_and_pumps,27.26
               nursing_home,TEK30,electrical_equipment,13.14
               nursing_home,TEK30,cooling,0.0
               hotel,TEK30,heating_rv,16.94
               hotel,TEK30,heating_dhw,16.76
               hotel,TEK30,fans_and_pumps,15.96
               hotel,TEK30,electrical_equipment,3.28
               hotel,TEK30,cooling,11.77
               sports,TEK30,heating_rv,18.26
               sports,TEK30,heating_dhw,27.57
               sports,TEK30,fans_and_pumps,9.92
               sports,TEK30,electrical_equipment,1.46
               sports,TEK30,cooling,0.0
               culture,TEK30,heating_rv,19.5
               culture,TEK30,heating_dhw,5.64
               culture,TEK30,fans_and_pumps,11.42
               culture,TEK30,electrical_equipment,1.61
               culture,TEK30,cooling,8.96
               storage_repairs,TEK30,heating_rv,25.27
               storage_repairs,TEK30,heating_dhw,5.64
               storage_repairs,TEK30,fans_and_pumps,8.5
               storage_repairs,TEK30,electrical_equipment,13.22
               storage_repairs,TEK30,cooling,8.16

   .. tab:: Download

        Download `energy_need_original_condition.csv <_static/user_case/tek30/energy_need_original_condition.csv>`_ complete with all building codes.


For clarity, the table above have been sorted and kwh_m2 values rounded to two decimal places.


Specify heating system shares
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The final input file that needs to be modified is :ref:`heating_system_initial_shares.csv<heating_system_initial_shares>`.
This file tells ``ebm`` what the share of each heating system is for a given building code. Since TEK30 is a new
building code, it requires its own definition in this file.


.. tabs::

   .. tab:: Summary table

        .. csv-table:: Summary heating_system_initial_shares.csv
           :header: building_category,building_code,heating_systems,year,heating_system_share

            office,TEK30,DH,2023,0.3182453573763764
            nursing_home,TEK30,DH - Bio,2023,0.0002142250969049
            office,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            school,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            school,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            school,TEK30,HP Central heating - Bio,2023,0.00019362655741
            kindergarten,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            …,…,…,…,…
            sports,TEK30,Electric boiler,2023,0.0596845137090352
            sports,TEK30,Electricity,2023,0.0706818896188211
            sports,TEK30,DH,2023,0.3182453573763764
            sports,TEK30,HP Central heating - Bio,2023,0.00019362655741
            sports,TEK30,HP - Electricity,2023,0.1632849356867121
            sports,TEK30,Electricity - Bio,2023,0.0216740945571909
            sports,TEK30,Gas,2023,0.0016565044759408
            sports,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            sports,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            sports,TEK30,Electric boiler - Solar,2023,0.0002493794096936

   .. tab:: formatted table

        .. csv-table:: Excerpt heating_system_initial_shares.csv
           :header: building_category,building_code,heating_systems,year,heating_system_share

            sports,TEK30,DH,2023,0.3182453573763764
            office,TEK30,DH,2023,0.3182453573763764
            nursing_home,TEK30,DH - Bio,2023,0.0002142250969049
            office,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            school,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            school,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            school,TEK30,HP Central heating - Bio,2023,0.00019362655741
            school,TEK30,HP - Electricity,2023,0.1632849356867121
            school,TEK30,Gas,2023,0.0016565044759408
            school,TEK30,Electricity - Bio,2023,0.0216740945571909
            school,TEK30,Electricity,2023,0.0706818896188211
            school,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            school,TEK30,Electric boiler,2023,0.0596845137090352
            school,TEK30,DH - Bio,2023,0.0002142250969049
            school,TEK30,DH,2023,0.3182453573763764
            retail,TEK30,DH,2023,0.3182453573763764
            retail,TEK30,DH - Bio,2023,0.0002142250969049
            retail,TEK30,Electric boiler,2023,0.0596845137090352
            retail,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            retail,TEK30,Electricity,2023,0.0706818896188211
            retail,TEK30,Electricity - Bio,2023,0.0216740945571909
            retail,TEK30,Gas,2023,0.0016565044759408
            retail,TEK30,HP - Electricity,2023,0.1632849356867121
            retail,TEK30,HP Central heating - Bio,2023,0.00019362655741
            retail,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            retail,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            office,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            nursing_home,TEK30,DH,2023,0.3182453573763764
            office,TEK30,HP Central heating - Bio,2023,0.00019362655741
            office,TEK30,Gas,2023,0.0016565044759408
            nursing_home,TEK30,Electric boiler,2023,0.0596845137090352
            nursing_home,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            nursing_home,TEK30,Electricity,2023,0.0706818896188211
            nursing_home,TEK30,Electricity - Bio,2023,0.0216740945571909
            nursing_home,TEK30,Gas,2023,0.0016565044759408
            nursing_home,TEK30,HP - Electricity,2023,0.1632849356867121
            nursing_home,TEK30,HP Central heating - Bio,2023,0.00019362655741
            nursing_home,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            nursing_home,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            house,TEK30,HP - Electricity,2023,0.0992947318980815
            house,TEK30,HP - Bio - Electricity,2023,0.5649908788840201
            house,TEK30,Electricity - Bio,2023,0.2247326376682365
            house,TEK30,Electricity,2023,0.0521984906804366
            house,TEK30,Electric boiler - Solar,2023,0.0003008594060781
            house,TEK30,Electric boiler,2023,0.0256775930931896
            house,TEK30,DH - Bio,2023,0.0076580066831269
            house,TEK30,DH,2023,0.0213315113565833
            sports,TEK30,DH - Bio,2023,0.0002142250969049
            office,TEK30,DH - Bio,2023,0.0002142250969049
            office,TEK30,Electric boiler,2023,0.0596845137090352
            office,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            office,TEK30,Electricity,2023,0.0706818896188211
            office,TEK30,Electricity - Bio,2023,0.0216740945571909
            office,TEK30,HP - Electricity,2023,0.1632849356867121
            sports,TEK30,Electric boiler,2023,0.0596845137090352
            storage_repairs,TEK30,DH,2023,0.3182453573763764
            sports,TEK30,Electricity,2023,0.0706818896188211
            hospital,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            hospital,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            university,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            university,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            university,TEK30,HP Central heating - Bio,2023,0.00019362655741
            university,TEK30,HP - Electricity,2023,0.1632849356867121
            university,TEK30,Gas,2023,0.0016565044759408
            university,TEK30,Electricity - Bio,2023,0.0216740945571909
            university,TEK30,Electricity,2023,0.0706818896188211
            university,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            university,TEK30,Electric boiler,2023,0.0596845137090352
            university,TEK30,DH - Bio,2023,0.0002142250969049
            university,TEK30,DH,2023,0.3182453573763764
            hospital,TEK30,HP Central heating - Bio,2023,0.00019362655741
            hotel,TEK30,DH,2023,0.3182453573763764
            hotel,TEK30,Electric boiler,2023,0.0596845137090352
            hotel,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            hotel,TEK30,Electricity,2023,0.0706818896188211
            hotel,TEK30,Electricity - Bio,2023,0.0216740945571909
            hotel,TEK30,Gas,2023,0.0016565044759408
            hotel,TEK30,HP - Electricity,2023,0.1632849356867121
            hotel,TEK30,HP Central heating - Bio,2023,0.00019362655741
            sports,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            hotel,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            house,TEK30,HP Central heating - Electric boiler,2023,0.0038152903302471
            storage_repairs,TEK30,Gas,2023,0.0016565044759408
            storage_repairs,TEK30,HP - Electricity,2023,0.1632849356867121
            storage_repairs,TEK30,HP Central heating - Bio,2023,0.00019362655741
            hotel,TEK30,DH - Bio,2023,0.0002142250969049
            hospital,TEK30,HP - Electricity,2023,0.1632849356867121
            hospital,TEK30,Gas,2023,0.0016565044759408
            hospital,TEK30,Electricity - Bio,2023,0.0216740945571909
            storage_repairs,TEK30,Electric boiler,2023,0.0596845137090352
            storage_repairs,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            storage_repairs,TEK30,Electricity,2023,0.0706818896188211
            storage_repairs,TEK30,Electricity - Bio,2023,0.0216740945571909
            culture,TEK30,DH,2023,0.3182453573763764
            culture,TEK30,DH - Bio,2023,0.0002142250969049
            culture,TEK30,Electric boiler,2023,0.0596845137090352
            culture,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            culture,TEK30,Electricity,2023,0.0706818896188211
            culture,TEK30,Electricity - Bio,2023,0.0216740945571909
            culture,TEK30,Gas,2023,0.0016565044759408
            culture,TEK30,HP - Electricity,2023,0.1632849356867121
            culture,TEK30,HP Central heating - Bio,2023,0.00019362655741
            culture,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            culture,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            apartment_block,TEK30,HP Central heating - Electric boiler,2023,0.1487089355849942
            apartment_block,TEK30,HP Central heating - Bio,2023,0.0086647944512573
            apartment_block,TEK30,HP - Electricity,2023,0.0073046316982173
            apartment_block,TEK30,Electricity - Bio,2023,0.1128016818166627
            apartment_block,TEK30,Electricity,2023,0.4560101624930742
            apartment_block,TEK30,Electric boiler - Solar,2023,0.0003390668680222
            apartment_block,TEK30,Electric boiler,2023,0.0560170260057814
            apartment_block,TEK30,DH - Bio,2023,0.0033946606308616
            apartment_block,TEK30,DH,2023,0.2067590404511287
            hospital,TEK30,DH,2023,0.3182453573763764
            hospital,TEK30,DH - Bio,2023,0.0002142250969049
            hospital,TEK30,Electric boiler,2023,0.0596845137090352
            hospital,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            hospital,TEK30,Electricity,2023,0.0706818896188211
            storage_repairs,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            storage_repairs,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            hotel,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            sports,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            sports,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            kindergarten,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            kindergarten,TEK30,Gas,2023,0.0016565044759408
            kindergarten,TEK30,HP - Electricity,2023,0.1632849356867121
            storage_repairs,TEK30,DH - Bio,2023,0.0002142250969049
            kindergarten,TEK30,DH,2023,0.3182453573763764
            kindergarten,TEK30,DH - Bio,2023,0.0002142250969049
            kindergarten,TEK30,Electric boiler,2023,0.0596845137090352
            kindergarten,TEK30,Electricity - Bio,2023,0.0216740945571909
            kindergarten,TEK30,Electricity,2023,0.0706818896188211
            kindergarten,TEK30,HP Central heating - Bio,2023,0.00019362655741
            kindergarten,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            sports,TEK30,HP Central heating - Bio,2023,0.00019362655741
            sports,TEK30,HP - Electricity,2023,0.1632849356867121
            sports,TEK30,Electricity - Bio,2023,0.0216740945571909
            sports,TEK30,Gas,2023,0.0016565044759408

   .. tab:: raw csv

        .. code-block:: csv

            sports,TEK30,DH,2023,0.3182453573763764
            office,TEK30,DH,2023,0.3182453573763764
            nursing_home,TEK30,DH - Bio,2023,0.0002142250969049
            office,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            school,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            school,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            school,TEK30,HP Central heating - Bio,2023,0.00019362655741
            school,TEK30,HP - Electricity,2023,0.1632849356867121
            school,TEK30,Gas,2023,0.0016565044759408
            school,TEK30,Electricity - Bio,2023,0.0216740945571909
            school,TEK30,Electricity,2023,0.0706818896188211
            school,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            school,TEK30,Electric boiler,2023,0.0596845137090352
            school,TEK30,DH - Bio,2023,0.0002142250969049
            school,TEK30,DH,2023,0.3182453573763764
            retail,TEK30,DH,2023,0.3182453573763764
            retail,TEK30,DH - Bio,2023,0.0002142250969049
            retail,TEK30,Electric boiler,2023,0.0596845137090352
            retail,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            retail,TEK30,Electricity,2023,0.0706818896188211
            retail,TEK30,Electricity - Bio,2023,0.0216740945571909
            retail,TEK30,Gas,2023,0.0016565044759408
            retail,TEK30,HP - Electricity,2023,0.1632849356867121
            retail,TEK30,HP Central heating - Bio,2023,0.00019362655741
            retail,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            retail,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            office,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            nursing_home,TEK30,DH,2023,0.3182453573763764
            office,TEK30,HP Central heating - Bio,2023,0.00019362655741
            office,TEK30,Gas,2023,0.0016565044759408
            nursing_home,TEK30,Electric boiler,2023,0.0596845137090352
            nursing_home,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            nursing_home,TEK30,Electricity,2023,0.0706818896188211
            nursing_home,TEK30,Electricity - Bio,2023,0.0216740945571909
            nursing_home,TEK30,Gas,2023,0.0016565044759408
            nursing_home,TEK30,HP - Electricity,2023,0.1632849356867121
            nursing_home,TEK30,HP Central heating - Bio,2023,0.00019362655741
            nursing_home,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            nursing_home,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            house,TEK30,HP - Electricity,2023,0.0992947318980815
            house,TEK30,HP - Bio - Electricity,2023,0.5649908788840201
            house,TEK30,Electricity - Bio,2023,0.2247326376682365
            house,TEK30,Electricity,2023,0.0521984906804366
            house,TEK30,Electric boiler - Solar,2023,0.0003008594060781
            house,TEK30,Electric boiler,2023,0.0256775930931896
            house,TEK30,DH - Bio,2023,0.0076580066831269
            house,TEK30,DH,2023,0.0213315113565833
            sports,TEK30,DH - Bio,2023,0.0002142250969049
            office,TEK30,DH - Bio,2023,0.0002142250969049
            office,TEK30,Electric boiler,2023,0.0596845137090352
            office,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            office,TEK30,Electricity,2023,0.0706818896188211
            office,TEK30,Electricity - Bio,2023,0.0216740945571909
            office,TEK30,HP - Electricity,2023,0.1632849356867121
            sports,TEK30,Electric boiler,2023,0.0596845137090352
            storage_repairs,TEK30,DH,2023,0.3182453573763764
            sports,TEK30,Electricity,2023,0.0706818896188211
            hospital,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            hospital,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            university,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            university,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            university,TEK30,HP Central heating - Bio,2023,0.00019362655741
            university,TEK30,HP - Electricity,2023,0.1632849356867121
            university,TEK30,Gas,2023,0.0016565044759408
            university,TEK30,Electricity - Bio,2023,0.0216740945571909
            university,TEK30,Electricity,2023,0.0706818896188211
            university,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            university,TEK30,Electric boiler,2023,0.0596845137090352
            university,TEK30,DH - Bio,2023,0.0002142250969049
            university,TEK30,DH,2023,0.3182453573763764
            hospital,TEK30,HP Central heating - Bio,2023,0.00019362655741
            hotel,TEK30,DH,2023,0.3182453573763764
            hotel,TEK30,Electric boiler,2023,0.0596845137090352
            hotel,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            hotel,TEK30,Electricity,2023,0.0706818896188211
            hotel,TEK30,Electricity - Bio,2023,0.0216740945571909
            hotel,TEK30,Gas,2023,0.0016565044759408
            hotel,TEK30,HP - Electricity,2023,0.1632849356867121
            hotel,TEK30,HP Central heating - Bio,2023,0.00019362655741
            sports,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            hotel,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            house,TEK30,HP Central heating - Electric boiler,2023,0.0038152903302471
            storage_repairs,TEK30,Gas,2023,0.0016565044759408
            storage_repairs,TEK30,HP - Electricity,2023,0.1632849356867121
            storage_repairs,TEK30,HP Central heating - Bio,2023,0.00019362655741
            hotel,TEK30,DH - Bio,2023,0.0002142250969049
            hospital,TEK30,HP - Electricity,2023,0.1632849356867121
            hospital,TEK30,Gas,2023,0.0016565044759408
            hospital,TEK30,Electricity - Bio,2023,0.0216740945571909
            storage_repairs,TEK30,Electric boiler,2023,0.0596845137090352
            storage_repairs,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            storage_repairs,TEK30,Electricity,2023,0.0706818896188211
            storage_repairs,TEK30,Electricity - Bio,2023,0.0216740945571909
            culture,TEK30,DH,2023,0.3182453573763764
            culture,TEK30,DH - Bio,2023,0.0002142250969049
            culture,TEK30,Electric boiler,2023,0.0596845137090352
            culture,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            culture,TEK30,Electricity,2023,0.0706818896188211
            culture,TEK30,Electricity - Bio,2023,0.0216740945571909
            culture,TEK30,Gas,2023,0.0016565044759408
            culture,TEK30,HP - Electricity,2023,0.1632849356867121
            culture,TEK30,HP Central heating - Bio,2023,0.00019362655741
            culture,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            culture,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            apartment_block,TEK30,HP Central heating - Electric boiler,2023,0.1487089355849942
            apartment_block,TEK30,HP Central heating - Bio,2023,0.0086647944512573
            apartment_block,TEK30,HP - Electricity,2023,0.0073046316982173
            apartment_block,TEK30,Electricity - Bio,2023,0.1128016818166627
            apartment_block,TEK30,Electricity,2023,0.4560101624930742
            apartment_block,TEK30,Electric boiler - Solar,2023,0.0003390668680222
            apartment_block,TEK30,Electric boiler,2023,0.0560170260057814
            apartment_block,TEK30,DH - Bio,2023,0.0033946606308616
            apartment_block,TEK30,DH,2023,0.2067590404511287
            hospital,TEK30,DH,2023,0.3182453573763764
            hospital,TEK30,DH - Bio,2023,0.0002142250969049
            hospital,TEK30,Electric boiler,2023,0.0596845137090352
            hospital,TEK30,Electric boiler - Solar,2023,0.0002493794096936
            hospital,TEK30,Electricity,2023,0.0706818896188211
            storage_repairs,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            storage_repairs,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            hotel,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            sports,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            sports,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            kindergarten,TEK30,HP Central heating - Gas,2023,7.196160696758601e-05
            kindergarten,TEK30,Gas,2023,0.0016565044759408
            kindergarten,TEK30,HP - Electricity,2023,0.1632849356867121
            storage_repairs,TEK30,DH - Bio,2023,0.0002142250969049
            kindergarten,TEK30,DH,2023,0.3182453573763764
            kindergarten,TEK30,DH - Bio,2023,0.0002142250969049
            kindergarten,TEK30,Electric boiler,2023,0.0596845137090352
            kindergarten,TEK30,Electricity - Bio,2023,0.0216740945571909
            kindergarten,TEK30,Electricity,2023,0.0706818896188211
            kindergarten,TEK30,HP Central heating - Bio,2023,0.00019362655741
            kindergarten,TEK30,HP Central heating - Electric boiler,2023,0.364043511904947
            sports,TEK30,HP Central heating - Bio,2023,0.00019362655741
            sports,TEK30,HP - Electricity,2023,0.1632849356867121
            sports,TEK30,Electricity - Bio,2023,0.0216740945571909
            sports,TEK30,Gas,2023,0.0016565044759408


Similarly to TEK17, there is no need to add TEK30 to :ref:`area.csv<area>` as all the area in both TEKs will be built after the start year 2020.


Re-run the model
^^^^^^^^^^^^^^^^

Once you have adapted building_code_parameters.csv, energy_need_original_condition.csv and heating_system_initial_shares.csv to TEK30, you cat re-run the model.

.. code-block:: powershell

   ebm --input=user-case-tek30

The model results can be found in the subdirectory named ``output``.

.. tip::

   You can have ebm open the results as they are written by using the ``--open`` option

   .. code-block:: powershell

      ebm --input=user-case-tek30 --open


Extra credit
^^^^^^^^^^^^

The input files :ref:`energy_need_improvements.csv<energy_need_improvements>`, :ref:`heating_system_forecast.csv<heating_system_forecast>`, :ref:`improvement_building_upgrade.csv<improvement_building_upgrade>` and :ref:`energy_need_behaviour_factor.csv<energy_need_behaviour_factor>`
have defined default values under the column building_code that will apply to TEK30. For extra credit you may override the defaults with your own values.


energy need improvements
""""""""""""""""""""""""

You can add a line to :ref:`energy_need_improvements.csv<energy_need_improvements>` if you think that there is no yearly reduction lighting with TEK30 .

.. code-block:: csv

   default,TEK30,lighting,yearly_reduction,2031,0.0,2050


energy need behaviour factor
""""""""""""""""""""""""""""

In :ref:`energy_need_behaviour_factor.csv<energy_need_behaviour_factor>` add TEK30 to the house row's building_code column:

This row:

.. code-block::

   house,TEK07+TEK10+TEK17,lighting,0.85,2020,noop,2050

Becomes:

.. code-block::

   house,TEK07+TEK10+TEK17+TEK30,lighting,0.85,2020,noop,2050

energy_need_original_condition
""""""""""""""""""""""""""""""

.. :ref:`user-case-tek30\energy_need_original_condition.csv<energy_need_original_condition>`
.. ``default``
.. ``ebm``

This file sets baseline lighting energy needs (kWh/m²) for different building types and codes used in the EBM model.

**default values**

.. csv-table:: energy_need_original_condition.csv where purpose is lighting
   :header: building_category,building_code,purpose,kwh_m2

    house,default,lighting,8.2
    apartment_block,default,lighting,8.2
    retail,default,lighting,50.2
    office,default,lighting,22.55
    kindergarten,default,lighting,18.79
    school,default,lighting,19.35
    university,default,lighting,22.55
    hospital,default,lighting,42.05
    nursing_home,default,lighting,42.05
    hotel,default,lighting,42.05
    sports,default,lighting,18.58
    culture,default,lighting,20.67
    storage_repairs,default,lighting,16.91

By default, all building codes have the same energy need for lighting per square metre. As an illustration on how one
can redefine energy need we will modify the file :ref:`user-case-tek30/energy_need_original_condition.csv<energy_need_original_condition>`.

If you open the file user-case-tek30/energy_need_original_condition.csv in a spreadsheet application or text editor,
you'll see that all building categories with lighting as their purpose use the building code "default."
This default value acts as a catch-all, telling EBM to apply the specified kWh/m²
value for lighting unless a more specific definition is provided.

.. csv-table:: Example energy_need_original_condition.csv
   :header: building_category,building_code,purpose,kwh_m2

    apartment_block,default,lighting,8.2
    house,default,lighting,8.2
    house,TEK17,lighting,5.0
    house,TEK10,lighting,6.2


**In this example**:

- All **apartment_block** buildings, regardless of code, use **8.2 kWh/m²** for lighting.
- **House** buildings also default to **8.2 kWh/m²**, except:

  - Houses with **TEK10** use **6.2 kWh/m²**
  - Houses with **TEK17** use **5.0 kWh/m²**




**Defining explicit lighting for TEK30**

While the default values for lighting in :ref:`energy_need_original_condition.csv<energy_need_original_condition>` are
handy for editing, you might want to set explicit values for TEK30 so that you can define specific values. Let's imagine
that the energy need for lighting with TEK30 is half of what earlier building code standards required.

.. csv-table:: Excerpt TEK30 lighting energy_need_original_condition.csv
   :header: building_category,building_code,purpose,kwh_m2

     house,TEK30,lighting,4.1
     apartment_block,TEK30,lighting,4.1
     retail,TEK30,lighting,25.1
     office,TEK30,lighting,11.27
     kindergarten,TEK30,lighting,9.4
     school,TEK30,lighting,8.2
     university,TEK30,lighting,11.26
     hospital,TEK30,lighting,21.03
     nursing_home,TEK30,lighting,21.03
     hotel,TEK30,lighting,21.0
     sports,TEK30,lighting,9.29
     culture,TEK30,lighting,10.34
     storage_repairs,TEK30,lighting,8.45


**Defining common lighting for TEK17 and TEK30**

To simplify energy need definitions across building codes, you can combine TEK17 and TEK30 using the + symbol. This
approach allows you to assign a shared lighting energy value to multiple building codes for the same building category.

You can also combine building categories in the same way. This is especially useful when several categories or codes
share identical lighting requirements, helping reduce duplication and streamline your definitions.

The example below demonstrates how to group both building codes and building categories that share the same lighting
energy need values.


.. csv-table:: Excerpt TEK30+TEK17 lighting energy_need_original_condition.csv
   :header: building_category,building_code,purpose,kwh_m2

    **apartment_block+house**,**TEK17+TEK30**,lighting,4.1
    retail,**TEK17+TEK30**,lighting,25.1
    office,**TEK17+TEK30**,lighting,11.27
    kindergarten,**TEK17+TEK30**,lighting,9.4
    school,**TEK17+TEK30**,lighting,8.2
    university,**TEK17+TEK30**,lighting,11.26
    **hospital+nursing_home+hotel**,**TEK17+TEK30**,lighting,11.01
    sports,**TEK17+TEK30**,lighting,9.29
    culture,**TEK17+TEK30**,lighting,10.34
    storage_repairs,**TEK17+TEK30**,lighting,8.45


.. |date| date::

Last Updated on |date|

Version: |version|.
