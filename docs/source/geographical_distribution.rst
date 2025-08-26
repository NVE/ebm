Geographical distribution
#############################

This page offers a comprehensive desciption of the ``ebmgeodist`` geographical distribution module in the EBM package.
The module geographically distributes EBM energy use projection results per each Norwegian municipality, providing a more detailed and
accurate representation of energy use patterns across the country.



Methods
=======

Elhub data has been used to find representative distribution keys for each Norwegian municipality. Elhub is a central data hub for Norway's power industry, and
the hub provides among other things, electricity consumption data per each measurement point for different regions and municipalities in Norway. Knowing the 
total electricity consumption per each municipality, we can find the corresponding share of electricity for that municipality. This share is then used as a 
distribution key to distribute the annual EBM energy use projection results. The geographical distribution module considers four different energy
types: electricity, district heating, bioenergy, and fossil fuels. Furthermore, three different building categories are included; households, holiday homes and 
commercial buildings. The distribution keys are either calculated directly from Elhub data
inside the module or loaded from input files under the ``input`` folder, depending on the energy type that is into consideration. The following table
gives an overview of the implemented functionality introduced in the module.

.. csv-table:: Geographical distribution overview
   :file: tables\geodist_implementation_combinations.csv
   :widths: 10 15 20 55
   :header-rows: 1


Detailed description
+++++++++++++++++++++

The following is a more detailed description of how the distribution keys for each energy type are obtained:

- Electricity: the distribution keys for electricity is calculated directly from Elhub data. The total electricity consumption per each municipality is divided
  by the total electricity consumption in Norway to get the share of electricity consumption for each municipality. This share is then used as a distribution key
  to distribute the annual EBM energy use projection results for electricity. The user can here choose between two options:

    - Generate the distribution keys using Elhub API inside the module, this assumes that the user has access to Elhub data via Azure Blob Storage.
    
    - Use the precalculated distribution keys provided by the input file under the ``input`` folder. The file name is 
      ``yearly_aggregated_elhub_data.parquet``. Accessing and loading the Elhub data directly from Azure Blob Storage will save the loaded data in a new 
      file with the same name but with an additional timestamp, under the ``input`` folder. The purpose of the timestamp is to distinguish between 
      different versions of the file. Later, the user may reuse this file to extract distribution keys rather than regenerating them via the Elhub API.

- District heating: the distribution keys for district heating are loaded from an input file under the ``input`` folder. The file name 
  is ``fjernvarme_kommune_fordelingsnøkler.xlsx``.

- Bioenergy: the distribution keys for bioenergy are loaded from an input file under the ``input`` folder. The file name is 
  is ``ved_kommune_fordelingsnøkler.xlsx``.

- Fossil fuels: the distribution keys for fossil fuels are loaded from an input file under the ``input`` folder. The file name is
  is ``ved_kommune_fordelingsnøkler.xlsx``.

Assumptions
===========

The geographical distribution module makes the following assumptions:

- The Elhub data used to calculate the distribution keys for electricity is representative for the entire projection period. Since the available Elhub
  data is from the year 2022 onwards, the module assumes that the electricity consumption patterns per municipality will remain relatively stable over time.
  The implemented method calculates an average electricity consumption per municipality based on the available Elhub data, and uses this average as 
  a distribution key for the entire projection period. This results static distribution keys for electricity that does not change over time.

- The electricity distribution keys for the moment do not take into account demographic changes, such as population growth or decline, which may affect electricity 
  consumption patterns in different municipalities over time. However, it is intended to implement a method that adjusts the electricity distribution keys
  based on projected demographic changes in future versions of the module.

- The distribution keys for district heating, bioenergy, and fossil fuels are assumed to be static and do not change over time. This means that the module assumes
  that the consumption patterns for these energy types will remain relatively stable over the projection period.

- For the energy type district heating, the holiday homes building category is not considered. This means that the module assumes that the 
  district heating consumption in holiday homes is negligible and does not significantly affect the overall distribution of district 
  heating consumption across municipalities. 

- For the energy type bioenergy, the commercial buildings building category is not considered. This means that the module assumes that the 
  bioenergy consumption in commercial buildings is negligible and does not significantly affect the overall distribution of bioenergy 
  consumption across municipalities.

- For the energy type fossil fuels, the households and commercial buildings building categories are not considered. This means that the module assumes that the
  fossil fuel consumption in households and commercial buildings is negligible and does not significantly affect the overall distribution of fossil fuel 
  consumption across municipalities.

- For the combination of bioenergy and holiday homes, the module assumes that the distribution keys for bioenergy consumption in holiday homes 
  are the same as for those for electricity and holiday homes. This assumption is made due to the lack of specific data on bioenergy consumption in holiday homes.

- For the combination of fossil fuels and holiday homes, the module assumes that the distribution keys for fossil fuel consumption in holiday homes 
  are the same as for those for electricity and holiday homes. This assumption is made due to the lack of specific data on fossil fuel consumption in holiday homes.

Limitations
===========


.. |date| date::

Last Updated on |date|

Version: |version|.