Assumptions
===========

The energy need in a buldings original condition is based on the energy requirement given by the building code. This energy requirement is one common value in in kWh per square. 
To get the energy need per energy purpose in the original condition, representative buildings per building category and building code
have been simulated in Simien. This work was originally done by Multiconsult in 2014 to simulate the energy purpose for buildings built built after different building codes to calculate a 
new building performance energy scale. There have been changes in the energy purpose since then, especially in lighting, due to new legislation from ecodesign. 
For more information on energy purpose in buildings see this summary report published in 2016 `Analyse av energibruk i yrkesbygg <https://publikasjoner.nve.no/rapport/2016/rapport2016_24.pdf>`_. 

In EBM 1.0 we assume that buildings undergo small measures and renovation over time. This reduces the energy need for the energy purpose space heating.

By default the model use an 60% improvement by the year 2030 for lighting. Electrical equipment has a yearly reduction of 1%. Lighting is expected to decrease by 0.5% yearly after 2030. 
These values are defined in :ref:`energy_need_improvements.csv <energy_need_improvements>`

It is assumed that only the heating need is reduced during an upgrade of the buildings. The heating need is reduced 
by 7 % in a building that undergoes small measures, by 15 % in a building that is renovated, and by 20 % in a building that undergoes 
both improvement measures.

As an example, we can look at office buildings built according to TEK 97. The calculations show that in 2024, 26 % of this 
area was in its original condition. This area is assigned the energy need that TEK 97 implies. The energy need is 
distributed by energy purpose by Multiconsult.  It is calculated that 62 % of the office area built according to TEK 97 has 
undergone small measures. This area is assigned energy need that corresponds to a 7 % reduction in the heating requirement 
compared to the requirements in TEK97. Similarly, the model shows that 12 % of the office area built according to TEK 97 was
renovated by 2024 and therefore is assigned energy need with a 15 % reduction in heating requirement compared to the energy 
need of building in its original condition.
