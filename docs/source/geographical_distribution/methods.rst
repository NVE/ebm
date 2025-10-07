Methods
=======

The geographical distribution method implemented in ``ebmgeodist`` provides a systematic way to allocate national or regional 
energy use projection results to finer geographical units, such as municipalities, counties, or grid areas.

Energy use models like EBM typically provide energy use projections at a national or regional level. However, for effective
energy planning and policy-making, results often need to be distributed to smaller geographical units. 
This method achieves this by distributing annual energy use projection to local scales while ensuring that the total energy use 
remains consistent with the original projections.

The method involves the following steps:

1. **Data Collection**: Gather relevant data on energy consumption patterns at the desired geographical level. This may include historical energy use data, 
   demographic information, and other relevant factors that influence energy consumption.

2. **Distribution Key Calculation**: Calculate distribution keys for each energy product (electricity, district heating, bioenergy, and fossil fuels) based on the collected data.
   
   These keys represent the share of total energy consumption attributed to each geographical unit.

3. **Energy Use Distribution**: Apply the distribution keys to the annual energy use projection results from EBM to allocate energy use to each geographical unit.

4. **Validation**: Validate the distributed results to ensure that they are consistent with known consumption patterns and that the total energy use remains unchanged.

5. **Output Generation**: Generate output files that contain the distributed energy use data for each geographical unit, which can be used for further analysis and planning.

The geographical distribution method is designed to be flexible and can be adapted to different geographical levels and energy products as needed.