# Input

To be run the EBM model, a number of files with data are required. These files can be modified to suit the result of 
different calculations, statistics and assumptions. As a rule of thumb most values can be modified, but when doing so, 
it is important the keep in mind what columns are used as identifiers. Apart from years, identifiers should remain
unchanged.

## area_parameters.csv

This file contain the total floor area (meters squared) built for each building category and TEK.

```csv
building_category, TEK, area
…
house, TEK97_RES, 19497955
kindergarten, PRE_TEK49_COM, 131242
…
```

### Identifiers

building_category and TEK are jointly used as identifiers. All values must be known by EBM.

 - building_category name of building category
 - TEK Available values are listed in TEK_ID.csv

#### Available building categories

house, apartment_block, kindergarten, school, university, office, retail, hotel, hospital, nursing_home, culture, sports, storage_repairs

### values

#### area

area is modifiable. area is expected to be represented by a whole number (integer). Floor area is combined with 
scurve_parameters.csv and used to predict the total floor area for each building category and building condition for a 
given year. 


## construction_building_category_yearly.csv

Lists built floor area for each building category by year. House and apartment block for the first two years. Other 
categories should define built floor area for the first 5 years.


```csv
year,house,apartment_block,kindergarten,school,…
2010,1807612,532779,97574,281884,112747,443334,…
…
2014,,,79992.0,256470.0,84340.0,320478.0,…
```

### Identifiers

 - year rows
 - building category columns

One building category for each column. One year for each row. The years must start at the model start year. There must
be five years for commercial buildings. There must be two years for residential buildings.

### values

 - area is modifiable. area is expected to be represented by a whole number (integer). For year three to five an empty value 
is expected for house and apartment_block.


## new_buildings_house_share.csv

This file contain the share between house and apartment block and square meter floor area for building categories for  
every year from the third model year until the end. The spelling mistake in flood_area_new_apartment_block must be left
as is. Please not that new_house_share and new_apartment_block_share is not compared in any way. It is a good idea to 
make sure the values add up to 1.0.

```csv 
"year",new_house_share,new_apartment_block_share,floor_area_new_house,flood_area_new_apartment_block
"2012","0.5320363954772",0.4679636045228,"175","75"
"2013","0.4949466591802","0.5050533408198","175","75"
…
"2050","0.4000000000000","0.6000000000000","175","75"
```

### Identifiers
 - year as a whole number (integer)

### values

- new_house_share are decimal numbers (float) between 0 and 1.
- new_apartment_block_share are decimal numbers (float) between 0 and 1.
- floor_area_new_house average floor area in square meters. Whole numbers (integer)
- flood_area_new_apartment_block average floor area in square meters. Whole numbers (integer)

floor_area_new_house and flood_area_new_apartment_block should work as decimal as well.

## new_buildings_population.csv

This file contain the total population and average household size per year. 

```csv
"year","population","household_size"
"2010","4858199","2.22"
"2011","4920305","2.22"
…
"2050","6001759","2.05"
```


### Identifier
 - year as a whole number (integer). Should have every year from model start to model end.

### values
 - population is a whole number (integer)
 - area is a decimal number 

## scurve_parameters.csv

## TEK_ID.csv

List of available TEK IDs. The file should be left as it is. 

```csv
TEK
PRE_TEK49_RES_1950
PRE_TEK49_RES_1940
PRE_TEK49_COM
TEK49_RES
TEK49_COM
TEK69_RES_1976
TEK69_RES_1986
TEK69_COM
TEK87_RES
TEK87_COM
TEK97_RES
TEK97_COM
TEK07
TEK10
TEK17
TEK21
```

### Identifiers
 - TEK 


## building_code.csv

This file contain assumed building year, period start year and period end year for every TEK. Every TEK in the model 
must have a entry here. Currently, the TEK21 end year must be the same as model end year. TEK07 building_year cannot be
smaller than the year after the model start year. 


```csv
TEK,building_year,period_start_year,period_end_year
PRE_TEK49_RES_1950,1950,0,1955
…
TEK07,2012,2013,2013
…
TEK21,2030,2025,2050
```

### Identifiers

 - TEK id of the TEK

### Values

 - building_year The assumed building year for the tek
 - period_start_year The first year for the TEK
 - period_end_year The last year for the TEK


## tekandeler.csv


```csv

building_category,TEK,Oppvarmingstyper,tek_share,Ekstralast andel,Grunnlast andel,Spisslast andel,Grunnlast virkningsgrad,Spisslast virkningsgrad,Ekstralast virkningsgrad,Tappevann virkningsgrad,Spesifikt elforbruk,Kjoling virkningsgrad
apartment_block,TEK07,Electricity,0.0,0.0,1.0,0.0,1.0,1.0,1,0.98,1,4
retail,TEK97,Electricity,0.08158166937579898,0.0,1.0,0.0,1.0,1.0,1,0.98,1,4
retail,PRE_TEK49,Electricity,0.07593898514970877,0.0,1.0,0.0,1.0,1.0,1,0.98,1,4
sports,TEK07,Electricity,0.06106588557516737,0.0,1.0,0.0,1.0,1.0,1,0.98,1,4


```

### Identifiers

 - building_category 
 - TEK
 - Oppvarmingstyper

### Values
 - tek_share
 - Ekstralast andel
 - Grunnlast andel
 - Spisslast andel
 - Grunnlast virkningsgrad
 - Spisslast virkningsgrad
 - Ekstralast virkningsgrad
 - Tappevann virkningsgrad
 - Spesifikt elforbruk
 - Kjoling virkningsgrad

