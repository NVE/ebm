User case
#########


This guide demonstrates how to create and configure a new scenario in EBM by introducing a hypothetical future building code: *TEK30*.
Scenario-based modeling in EBM allows users to explore alternative planning assumptions, regulatory changes, and energy performance impacts by managing separate input directories.

The TEK30 scenario showcases how to:
 - Create a dedicated input directory for scenario data
 - Define a new building code and its timeline
 - Specify energy needs across building categories
 - Configure heating system shares
 - Optionally adjust lighting improvements


Working with input
==================

EBM supports scenario-based modeling by allowing users to create and manage separate input directories. This enables
flexible experimentation with different assumptions and configurations.


Creating an input directory for a scenario
++++++++++++++++++++++++++++++++++++++++++

To create a new scenario in EBM, open your preferred terminal and run the following command:

.. code-block:: bash

   ebm --create-input --input=user-case-tek30


The input directory will be created path defined after `--input==`. In this case the files will be added to the
subdirectory `user-case-tek30`.
If the directory you name does not already exist, the program will attempt to create it. All input files necessary to run ebm will be created, with their default values, in the supplied path.


.. tip::

    You can choose any valid directory name, but it is a good idea to limit to letters, numbers, and underscore. Avoid using space.





Using the input directory
+++++++++++++++++++++++++

Once the input directory is ready, you can run the model using:

.. code-block:: bash

   ebm --input=user-case-tek30

The model result as defined in with user-case-tek30 will be written to the subdirectory ``output``.

.. seealso::

   :ref:`Results <results>`


User case: Add a new building code
==================================

This example demonstrates how to use EBM’s scenario functionality by adding a new building code. TEK30 represents
a hypothetical future building code introduced as part of a user case to demonstrate how EBM handles scenario-based
modeling.


To add TEK30 to ebm you will need to
 - :ref:`Add the new building code to the model in building_code_parameters.csv<add the new building code>`
 - :ref:`Define energy needs for TEK30 in energy_need_original_condition.csv<define energy needs for TEK30>`
 - :ref:`Specify heating system shares in heating_system_initial_shares.csv<Specify heating system shares>`


This process showcases how EBM can be extended to simulate future regulations or alternative planning assumptions.


Add the new building code
+++++++++++++++++++++++++

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
     - building_year: 2030
     - period_start_year: 2030
     - period_end_year: 2050

Add the following line to building_code_parameters.csv to define TEK30 as a new building code entry:

.. code-block:: text

   TEK30,2030,2030,2050


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
           **TEK30**,**2030**,**2030**,**2050**

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
            TEK30,2030,2030,2050

   .. tab:: Download

        Optionally, `Download building_code_parameters.csv <_static/user_case/tek30/building_code_parameters.csv>`_ working example.

Define energy needs for TEK30
+++++++++++++++++++++++++++++

All building codes must have it's energy need defined in energy_need_original_condition.csv.

.. tabs::

   .. tab:: Summary table

        Open *formatted table* and *raw csv* for complete listings

        .. csv-table:: Summary energy_need_original_condition.csv
           :header: building_category,building_code,purpose,kwh_m2

                office,TEK30,cooling,15.44310555555556
                university,TEK30,cooling,19.2249
                sports,TEK30,cooling,0.0
                office,TEK30,heating_rv,25.89288134147665
                office,TEK30,electrical_equipment,34.45833333333334
                …,…,…,…
                hospital,TEK30,electrical_equipment,46.72
                hospital,TEK30,cooling,30.77232222222222
                kindergarten,TEK30,heating_rv,74.22534704119848
                kindergarten,TEK30,fans_and_pumps,22.46678333333334
                hospital,TEK30,heating_rv,78.03709182765022
                kindergarten,TEK30,heating_dhw,10.02333333333333

   .. tab:: Formatted table

        You should be able to paste the content of this table into energy_need_original_condition.csv when using Excel

        .. csv-table:: Excerpt energy_need_original_condition.csv
           :header: building_category,building_code,purpose,kwh_m2

                office,TEK30,cooling,15.44310555555556
                university,TEK30,cooling,19.2249
                sports,TEK30,cooling,0.0
                office,TEK30,heating_rv,25.89288134147665
                office,TEK30,electrical_equipment,34.45833333333334
                university,TEK30,electrical_equipment,34.45833333333334
                sports,TEK30,heating_dhw,49.02
                sports,TEK30,heating_rv,54.79322499007694
                office,TEK30,heating_dhw,5.011111111111111
                university,TEK30,heating_dhw,5.011111111111111
                university,TEK30,fans_and_pumps,19.49136035
                office,TEK30,fans_and_pumps,16.24322837777778
                sports,TEK30,fans_and_pumps,17.6285983125
                sports,TEK30,electrical_equipment,2.58
                retail,TEK30,cooling,29.89947777777778
                retail,TEK30,electrical_equipment,3.743888888888889
                school,TEK30,cooling,0.0
                school,TEK30,electrical_equipment,12.9
                school,TEK30,fans_and_pumps,23.91209403333333
                school,TEK30,heating_dhw,9.804166666666667
                school,TEK30,heating_rv,46.01008020969308
                storage_repairs,TEK30,heating_rv,75.81893646684172
                storage_repairs,TEK30,fans_and_pumps,15.11833333333333
                university,TEK30,heating_rv,25.59177873258427
                nursing_home,TEK30,heating_dhw,29.78416666666667
                nursing_home,TEK30,electrical_equipment,23.36
                nursing_home,TEK30,cooling,0.0
                storage_repairs,TEK30,electrical_equipment,23.49
                storage_repairs,TEK30,cooling,14.51195
                retail,TEK30,heating_rv,49.66536669467513
                retail,TEK30,heating_dhw,10.48333333333333
                retail,TEK30,fans_and_pumps,39.77525066666666
                nursing_home,TEK30,fans_and_pumps,48.44664545
                storage_repairs,TEK30,heating_dhw,10.0225
                nursing_home,TEK30,heating_rv,90.03560739873801
                hospital,TEK30,fans_and_pumps,43.3837432
                hotel,TEK30,cooling,20.92845
                apartment_block,TEK30,cooling,0.0
                apartment_block,TEK30,electrical_equipment,17.52
                apartment_block,TEK30,fans_and_pumps,7.566666666666666
                apartment_block,TEK30,heating_dhw,29.76888888888889
                apartment_block,TEK30,heating_rv,28.84117055278729
                house,TEK30,heating_dhw,29.78125
                hotel,TEK30,electrical_equipment,5.84
                hotel,TEK30,fans_and_pumps,28.3693625
                kindergarten,TEK30,cooling,0.0
                hotel,TEK30,heating_dhw,29.78416666666667
                culture,TEK30,heating_rv,58.50821023656364
                culture,TEK30,heating_dhw,10.0225
                culture,TEK30,fans_and_pumps,20.29445719583333
                culture,TEK30,electrical_equipment,2.870833333333333
                culture,TEK30,cooling,15.93465
                hospital,TEK30,heating_dhw,29.76944444444445
                house,TEK30,cooling,0.0
                house,TEK30,electrical_equipment,17.51875
                house,TEK30,heating_rv,47.48088503199805
                hotel,TEK30,heating_rv,50.81432489054104
                kindergarten,TEK30,electrical_equipment,5.22
                house,TEK30,fans_and_pumps,6.407520999999999
                hospital,TEK30,electrical_equipment,46.72
                hospital,TEK30,cooling,30.77232222222222
                kindergarten,TEK30,heating_rv,74.22534704119848
                kindergarten,TEK30,fans_and_pumps,22.46678333333334
                hospital,TEK30,heating_rv,78.03709182765022
                kindergarten,TEK30,heating_dhw,10.02333333333333

   .. tab:: Raw csv

        You can add the raw excel content at the end of energy_need_original_condition.csv using notepad or a similar text editor.

        .. code-block:: text

            office,TEK30,cooling,15.44310555555556
            university,TEK30,cooling,19.2249
            sports,TEK30,cooling,0.0
            office,TEK30,heating_rv,25.89288134147665
            office,TEK30,electrical_equipment,34.45833333333334
            university,TEK30,electrical_equipment,34.45833333333334
            sports,TEK30,heating_dhw,49.02
            sports,TEK30,heating_rv,54.79322499007694
            office,TEK30,heating_dhw,5.011111111111111
            university,TEK30,heating_dhw,5.011111111111111
            university,TEK30,fans_and_pumps,19.49136035
            office,TEK30,fans_and_pumps,16.24322837777778
            sports,TEK30,fans_and_pumps,17.6285983125
            sports,TEK30,electrical_equipment,2.58
            retail,TEK30,cooling,29.89947777777778
            retail,TEK30,electrical_equipment,3.743888888888889
            school,TEK30,cooling,0.0
            school,TEK30,electrical_equipment,12.9
            school,TEK30,fans_and_pumps,23.91209403333333
            school,TEK30,heating_dhw,9.804166666666667
            school,TEK30,heating_rv,46.01008020969308
            storage_repairs,TEK30,heating_rv,75.81893646684172
            storage_repairs,TEK30,fans_and_pumps,15.11833333333333
            university,TEK30,heating_rv,25.59177873258427
            nursing_home,TEK30,heating_dhw,29.78416666666667
            nursing_home,TEK30,electrical_equipment,23.36
            nursing_home,TEK30,cooling,0.0
            storage_repairs,TEK30,electrical_equipment,23.49
            storage_repairs,TEK30,cooling,14.51195
            retail,TEK30,heating_rv,49.66536669467513
            retail,TEK30,heating_dhw,10.48333333333333
            retail,TEK30,fans_and_pumps,39.77525066666666
            nursing_home,TEK30,fans_and_pumps,48.44664545
            storage_repairs,TEK30,heating_dhw,10.0225
            nursing_home,TEK30,heating_rv,90.03560739873801
            hospital,TEK30,fans_and_pumps,43.3837432
            hotel,TEK30,cooling,20.92845
            apartment_block,TEK30,cooling,0.0
            apartment_block,TEK30,electrical_equipment,17.52
            apartment_block,TEK30,fans_and_pumps,7.566666666666666
            apartment_block,TEK30,heating_dhw,29.76888888888889
            apartment_block,TEK30,heating_rv,28.84117055278729
            house,TEK30,heating_dhw,29.78125
            hotel,TEK30,electrical_equipment,5.84
            hotel,TEK30,fans_and_pumps,28.3693625
            kindergarten,TEK30,cooling,0.0
            hotel,TEK30,heating_dhw,29.78416666666667
            culture,TEK30,heating_rv,58.50821023656364
            culture,TEK30,heating_dhw,10.0225
            culture,TEK30,fans_and_pumps,20.29445719583333
            culture,TEK30,electrical_equipment,2.870833333333333
            culture,TEK30,cooling,15.93465
            hospital,TEK30,heating_dhw,29.76944444444445
            house,TEK30,cooling,0.0
            house,TEK30,electrical_equipment,17.51875
            house,TEK30,heating_rv,47.48088503199805
            hotel,TEK30,heating_rv,50.81432489054104
            kindergarten,TEK30,electrical_equipment,5.22
            house,TEK30,fans_and_pumps,6.407520999999999
            hospital,TEK30,electrical_equipment,46.72
            hospital,TEK30,cooling,30.77232222222222
            kindergarten,TEK30,heating_rv,74.22534704119848
            kindergarten,TEK30,fans_and_pumps,22.46678333333334
            hospital,TEK30,heating_rv,78.03709182765022
            kindergarten,TEK30,heating_dhw,10.02333333333333

   .. tab:: Download

        `Download energy_need_original_condition.csv <_static/user_case/tek30/energy_need_original_condition.csv>`_

Specify heating system shares
+++++++++++++++++++++++++++++

Finally `heating_system_initial_shares.csv` must have heating system share defined for TEK30.

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


Optionally, you can add a line to `energy_need_improvements.csv` if you think that there is no yearly reduction lighting with TEK30 .


.. code-block:: csv

   default,TEK30,lighting,yearly_reduction,2031,0.0,2050


Similarly to TEK17, there is no need to add TEK30 to ``area.csv`` as all the area in both TEKs will be built after the start year 2020.


Extra credit
++++++++++++

The input files ``heating_system_forecast.csv``, ``improvement_building_upgrade.csv`` and ``energy_need_behaviour_factor.csv``
have defined default values under the column building_code that will apply to TEK30. For extra credit you may override the defaults with your own values.

Example:

In ``energy_need_behaviour_factor.csv`` add TEK30 to the house row's building_code column:

This row:

.. code-block::

   house,TEK07+TEK10+TEK17,lighting,0.85,2020,noop,2050

Becomes:

.. code-block::

   house,TEK07+TEK10+TEK17+TEK30,lighting,0.85,2020,noop,2050




Troubleshooting
+++++++++++++++

.. admonition:: Suggested issues for troubleshooting

    - FileNotFoundError: No such directory usercase_tek33 (missing input directory)
    - Could not find building_code_parameters.csv (missing input file)
    - building_code periods do not overlap failure cases: TEK10, 2018, 2011, 2021 (overlapping building codes)
    - PermissionError: [Errno 13] Permission denied: 'output\\demolition_construction.xlsx' (file open)
    - period_end_year should be greater than period_start_year> failure cases: PRE_TEK49;1945;0;1948" (Semi colon as delimiter)



.. |date| date::

Last Updated on |date|

Version: |version|.
