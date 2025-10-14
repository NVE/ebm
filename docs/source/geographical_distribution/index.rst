Geographical distribution
#############################

This page offers a comprehensive description of the ``ebmgeodist`` geographical distribution module in the EBM package.
The module provides functionality to distribute the national energy use results from EBM down to energy use per municipality,
providing a more detailed and accurate representation of energy use patterns across the country.

.. contents:: Table of Contents
   :depth: 2
   :local:
   :backlinks: none


Model functionality
=====================

The geographical distribution method implemented in ``ebmgeodist`` provides a systematic way to allocate national or regional 
energy use projection results to finer geographical units — in our case, municipalities.

Energy use models like EBM typically provide energy use forecasts at a national or regional level. However, for effective
energy planning and policy-making, results often need to be distributed to smaller geographical units. 
This method achieves this by distributing annual energy use forecasts to a smaller geographical area, while ensuring that the total energy use 
remains consistent with the national results.

The method involves the following steps:

1. **Data Collection**: Gather relevant statistics on energy consumption at the desired geographical level. This may include historical energy use data, 
   demographic information, and other relevant factors that influence energy consumption.

2. **Distribution Key Calculation**: Calculate distribution keys for each energy product (electricity, district heating, bioenergy, and fossil fuels) based on the collected data.

.. math::

   f_{m,g} = \frac{C_{m,g}}{\Sigma_{j\in all \, municipalities}C_{j,g}}
   

Where :math:`f_{m,g}` is the distribution key for municipality *m* and building category *g*, :math:`C_{m,g}` is the total consumption for municipality *m* and building category *g*, 
and the denominator is representing the total consumption for all municipalities and building category g.


These keys represent the share of total energy consumption attributed to each geographical unit.

3. **Energy Use Distribution**: Apply the distribution keys to the annual energy use forecast results from EBM to allocate energy use to each geographical unit:

.. math::

   \text{Consumption}_{m,g} = f_{m,g} \: \mathsf x \: \text{National total}_{g}


4. **Validation**: Validate the distributed results to ensure that they are consistent with consumption statistics and that the total national energy use remains unchanged.

5. **Output Generation**: Generate output files that contain the distributed energy use data for each geographical unit, which can be used for further analysis and planning.

The geographical distribution method is designed to be flexible and can be adapted to different geographical levels and energy products as needed.


Assumptions
===========


Elhub data has been used to find representative distribution keys for each Norwegian municipality. Elhub is a central data hub for Norway's power industry, and
the hub provides among other things, electricity consumption data per each measurement point for different regions and municipalities in Norway. Knowing the 
total electricity consumption for residential, holiday home, and non-residential buildings categories in each municipality, we can find the corresponding share of electricity for that municipality
compared to the national level. This share is then used as a key to distribute the annual forecasted EBM energy use results. The geographical distribution module considers four different energy
products: electricity, district heating, bioenergy, and fossil fuels. Furthermore, three different building categories are included; residential, holiday homes and 
non-residential buildings. The distribution keys for electricity are generated inside the module, either using Elhub API or using attached consumption data stored in the file |elhub_aggregated_data_ref| under |input_directory|.
The Elhub API option assumes that the user has access to Elhub data via Azure Blob Storage. 
As for the other energy products, the distribution keys are loaded from input files under |input_directory|. The input files are provided along with the module.
The following table gives an overview of the implemented functionality introduced in the module, including the input files for each energy product:

.. csv-table:: Geographical distribution overview
   :file: ..\tables\geodist_implementation_combinations.csv
   :widths: 10 15 20 55
   :header-rows: 1


Detailed description
--------------------

The following is a more detailed description of how the distribution keys for each energy product are obtained:

- Electricity: the distribution keys for electricity is calculated directly from Elhub data. The total electricity consumption per each municipality is divided
  by the total electricity consumption in Norway to get the share of electricity consumption for each municipality. This share is then used as a distribution key
  to distribute the annual EBM energy use projection results for electricity. The user can here choose between two options:

    - Generate the distribution keys using Elhub API inside the module, this assumes that the user has access to Elhub data via Azure Blob Storage.
    
    - Use the precalculated distribution keys provided by the input file under the ``input`` folder. The file name is 
      ``yearly_aggregated_elhub_data.parquet``. Accessing and loading the Elhub data directly from Azure Blob Storage will save the loaded data in a new 
      file with the same name but with an additional timestamp, under the ``input`` folder. The purpose of the timestamp is to distinguish between 
      different versions of the file. Later, the user may reuse this new file to extract distribution keys rather than regenerating them via the Elhub API.

- District heating: the distribution keys for district heating are loaded from an input file under the ``input`` folder. The file name 
  is ``fjernvarme_kommune_fordelingsnøkler.xlsx``.

- Bioenergy: the distribution keys for bioenergy are loaded from an input file under the ``input`` folder. The file name is 
  is ``ved_kommune_fordelingsnøkler.xlsx``.

- Fossil fuels: the distribution keys for fossil fuels are loaded from an input file under the ``input`` folder. The file name is
  is ``ved_kommune_fordelingsnøkler.xlsx``.



The geographical distribution module makes the following assumptions:

- The Elhub data used to calculate the distribution keys for electricity is representative for the entire projection period. Since the available Elhub
  data is from the year 2022 onwards, the module assumes that the electricity consumption patterns per municipality will remain relatively stable over time.
  The implemented method calculates an average electricity consumption per municipality based on the available Elhub data, and uses this average to find
  distribution keys for the entire projection period. This results in static distribution keys for electricity that does not change over time.

- The electricity distribution keys for the moment do not take into account demographic changes, such as population growth or decline, which may affect electricity 
  consumption patterns in different municipalities over time. However, it is intended to implement a method that adjusts the electricity distribution keys
  based on projected demographic changes in future versions of the module.

- The distribution keys for district heating, bioenergy, and fossil fuels are assumed to be static and do not change over time. This means that the module assumes
  that the consumption patterns for these energy products will remain relatively stable over the projection period.

- For district heating, the holiday homes building category is not considered. This means that the module assumes that the 
  district heating consumption in holiday homes is negligible and does not significantly affect the overall distribution of district 
  heating consumption across municipalities. 

- For bioenergy, the commercial buildings building category is not considered. This means that the module assumes that the 
  bioenergy consumption in commercial buildings is negligible and does not significantly affect the overall distribution of bioenergy 
  consumption across municipalities.

- For fossil fuels, the households and commercial buildings categories are not included. This is not because their consumption is assumed to be negligible, but 
  because the module currently lacks reliable data to calculate distribution keys for these categories.

- For the combination of bioenergy and holiday homes, the module assumes that the distribution keys for bioenergy consumption in holiday homes 
  are the same as for those for electricity and holiday homes. This assumption is made due to the lack of specific data on bioenergy consumption in holiday homes.

- For the combination of fossil fuels and holiday homes, the module assumes that the distribution keys for fossil fuel consumption in holiday homes 
  are the same as for those for electricity and holiday homes. This assumption is made due to the lack of specific data on fossil fuel consumption in holiday homes.


Limitations
===========


The geographical distribution module has the following limitations:

- Currently, the module distributes annual EBM energy use projection results only at the municipality level. However, future versions are intended to support
  additional levels of geographical distribution, such as price areas and grid zones.

- Distribution keys for electricity can only be generated via the Elhub API for years from 2022 onwards, since Elhub data is available only 
  from that year.

- The module does not currently account for demographic changes, such as population growth or decline, which may affect electricity consumption patterns.
  However, it is intended to implement a method that adjusts the electricity distribution keys based on projected demographic changes in future versions 
  of the module.
  
  
.. |date| date::

Last Updated on |date|

Version: |version|.
