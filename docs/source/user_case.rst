User case
#########


.. note::

   DRAFT


Scenario
========
How to create different scenarios through a user case. 


EBM has built in support for making and using different directories as it's input.

Creating a new scenario
+++++++++++++++++++++++

To create a new scenario with EBM the default input use the command:

.. code-block:: bash

   ebm --create-input --input=input_tek30


Running a scenario
++++++++++++++++++

To run the model with the new scenario you can use

.. code-block:: bash

   ebm --input=input_tek30


Adding new building code TEK30
++++++++++++++++++++++++++++++

Add tek30 to building_code_parameters.csv with building_year and period_start_year set to 2030 and period_end_year set to 2050.

.. code-block:: csv

   TEK30,2030,2030,2050


EBM does not allow  overlapping periods in building_code_parameters.csv. So we must also change the period end year for TEK17 from 2050 to 2029.

.. code-block:: csv

   TEK17,2025,2020,2029


.. tabs::

   .. tab:: Formatted table

        Tekst inni fane DRAFT

        .. csv-table:: Complete building_code_parameters.csv
           :header: "building_code", "building_year", "period_start_year", "period_end_year"
           :widths: 11, 6, 6, 6

           PRE_TEK49, 1945, 0, 1948
           TEK49,1962,1949,1968
           TEK69,1977,1969,1986
           TEK87,1991,1987,1996
           TEK97,2002,1997,2006
           TEK07,2012,2007,2010
           TEK10,2018,2011,2019
           TEK17,2025,2020,**2029**
           **TEK30**,**2030**,**2030**,**2050**

   .. tab:: Raw CSV

        bla bla bla

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


All building codes must have it's energy need defined in energy_need_original_condition.csv.

.. tabs::

   .. tab:: Summary table

        bla bla bla

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

        bla bla bla

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

        Add this CSV text to the end of energy_need_original_condition.csv

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




Finally `heating_system_initial_shares.csv` must have heating system share defined for TEK30.

.. tabs::

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





Similarly to TEK17 there is no need to add TEK30 to `area.csv` as all the area will built after the start year 2020.


Optionally, add a line to `energy_need_improvements_tek30.csv` if you think there is no yearly_reduction for TEK30 lighting.


.. code-block:: csv

   default,TEK30,lighting,yearly_reduction,2031,0.0,2050





.. |date| date::

Last Updated on |date|

Version: |version|.
