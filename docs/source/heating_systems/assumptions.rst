Assumptions
===========

Initial shares
--------------
During calculation of the intial shares about 130 000 certificates from the building energy performance database do not have information about the
buildings heating system. The certificates have information on "delivered energy" for various energy products. All the delivered energy coulumns are 
put together and an aggregation is made to create the most common combinations. Oil based heating was banned in 2020, but the database contains a lot of 
certificates issued before this ban. For the intiial shares we assume that half of the buildings who used oil-based heating switch to electric boilers and
the other half to a water-borne heatpump.  

The building energy performance database gives us information on heating systems across the various building codes. However for some building categories,
especially for newer building codes, the amount of certificates are too few to give a good representation of that particular building code and category. 
We therefore assume that the distribution of heating systems are the same across all non-residential buildings and building codes. The same assumption
is made for residential buildings, but are different for houses and for apartments.

Forecasting
-----------
The current implementation and numbers of forecasting heating systems is based on various assumptions. The first assumption is that natural gas is phased out as a heating
system for buildings by 2030. The second assumption is the continued growth of air-air heat pumps in houses. The final assumption is an increase in water-borne 
heating in new apartment blocks and non-residential buildings from building code requirements. The last assumption is causes an increase in electric boilers and 
central heating heat pumps. The final assumption is that the share of distrcit heating will increase in both non-residental buildings and in apartment blocks. 