# Tek-andeler


```python

from pd_config import pd, logger
pd.set_option('display.float_format', '{:.3f}'.format)


```


```python
from ebm.model.filter_tek import FilterTek
from ebm.model import BuildingCategory, DatabaseManager
from ebm.model.energy_purpose import EnergyPurpose
from ebm.model.data_classes import YearRange

from ebm.cmd.run_calculation import calculate_building_category_energy_requirements, calculate_building_category_area_forecast
```

## Load energy requirement into df


```python
from ebm.cmd.run_calculation import area_forecast_result_to_dataframe

dm = DatabaseManager()
period = YearRange(2010, 2050)
energy_requirements = []
for building_category in BuildingCategory:
    #if building_category != BuildingCategory.KINDERGARTEN:
    #    continue
    logger.info(f'Energy requirements for {building_category}')
    area_forecast = calculate_building_category_area_forecast(building_category=building_category,
                                                              database_manager=dm,
                                                              start_year=period.start,
                                                              end_year=period.end)
    a_df = area_forecast_result_to_dataframe(building_category, area_forecast, period.start, period.end)


    req_df = calculate_building_category_energy_requirements(building_category, a_df, dm, period.start, period.end)
    #req_df.rename(columns={'tek': 'TEK'}, inplace=True)
    req_df = req_df.reset_index()
    req_df.tek = req_df.tek.apply(lambda s: s.replace('_COM', '').replace('_RES', ''))
    #req_df.tek.set_index(['building_category', 'building_condition', 'purpose', 'tek', 'year'])

    req_df = req_df.set_index(['building_category', 'building_condition', 'purpose', 'tek', 'year'])
    energy_requirements.append(req_df)

df = pd.concat(energy_requirements)
df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th>m2</th>
      <th>kwh_m2</th>
      <th>energy_requirement</th>
    </tr>
    <tr>
      <th>building_category</th>
      <th>building_condition</th>
      <th>purpose</th>
      <th>tek</th>
      <th>year</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">house</th>
      <th rowspan="5" valign="top">original_condition</th>
      <th>heating_rv</th>
      <th>PRE_TEK49_1940</th>
      <th>2010</th>
      <td>1569144.291</td>
      <td>155.291</td>
      <td>243673534.212</td>
    </tr>
    <tr>
      <th>heating_dhw</th>
      <th>PRE_TEK49_1940</th>
      <th>2010</th>
      <td>1569144.291</td>
      <td>29.781</td>
      <td>46731078.417</td>
    </tr>
    <tr>
      <th>fans_and_pumps</th>
      <th>PRE_TEK49_1940</th>
      <th>2010</th>
      <td>1569144.291</td>
      <td>0.581</td>
      <td>912065.119</td>
    </tr>
    <tr>
      <th>lighting</th>
      <th>PRE_TEK49_1940</th>
      <th>2010</th>
      <td>1569144.291</td>
      <td>9.110</td>
      <td>14294904.491</td>
    </tr>
    <tr>
      <th>electrical_equipment</th>
      <th>PRE_TEK49_1940</th>
      <th>2010</th>
      <td>1569144.291</td>
      <td>17.519</td>
      <td>27489446.548</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">storage_repairs</th>
      <th rowspan="5" valign="top">renovation_and_small_measure</th>
      <th>heating_dhw</th>
      <th>TEK21</th>
      <th>2050</th>
      <td>0.000</td>
      <td>10.023</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>fans_and_pumps</th>
      <th>TEK21</th>
      <th>2050</th>
      <td>0.000</td>
      <td>15.118</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>lighting</th>
      <th>TEK21</th>
      <th>2050</th>
      <td>0.000</td>
      <td>5.100</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>electrical_equipment</th>
      <th>TEK21</th>
      <th>2050</th>
      <td>0.000</td>
      <td>17.202</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>cooling</th>
      <th>TEK21</th>
      <th>2050</th>
      <td>0.000</td>
      <td>14.512</td>
      <td>0.000</td>
    </tr>
  </tbody>
</table>
</div>



### Normalize TEK names


```python

```

# Sjekk TEK69 for residential


```python

```


```python

df = FilterTek.merge_tek(df, 'TEK69', ['TEK69_1976', 'TEK69_1986'])
df = FilterTek.merge_tek(df, 'PRE_TEK49', ['PRE_TEK49_1940', 'PRE_TEK49_1950'])
df = df.sort_index()
df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th>m2</th>
      <th>kwh_m2</th>
      <th>energy_requirement</th>
    </tr>
    <tr>
      <th>building_category</th>
      <th>building_condition</th>
      <th>purpose</th>
      <th>tek</th>
      <th>year</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">apartment_block</th>
      <th rowspan="5" valign="top">original_condition</th>
      <th rowspan="5" valign="top">cooling</th>
      <th rowspan="5" valign="top">PRE_TEK49</th>
      <th>2010</th>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>2011</th>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>2012</th>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>2013</th>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>2014</th>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">university</th>
      <th rowspan="5" valign="top">small_measure</th>
      <th rowspan="5" valign="top">lighting</th>
      <th rowspan="5" valign="top">TEK97</th>
      <th>2046</th>
      <td>267379.867</td>
      <td>9.250</td>
      <td>2473270.696</td>
    </tr>
    <tr>
      <th>2047</th>
      <td>262714.941</td>
      <td>9.204</td>
      <td>2417969.416</td>
    </tr>
    <tr>
      <th>2048</th>
      <td>258050.016</td>
      <td>9.158</td>
      <td>2363159.317</td>
    </tr>
    <tr>
      <th>2049</th>
      <td>253385.091</td>
      <td>9.112</td>
      <td>2308836.869</td>
    </tr>
    <tr>
      <th>2050</th>
      <td>248720.165</td>
      <td>9.066</td>
      <td>2254998.567</td>
    </tr>
  </tbody>
</table>
</div>




```python

```


```python



```


```python
df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th>m2</th>
      <th>kwh_m2</th>
      <th>energy_requirement</th>
    </tr>
    <tr>
      <th>building_category</th>
      <th>building_condition</th>
      <th>purpose</th>
      <th>tek</th>
      <th>year</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">apartment_block</th>
      <th rowspan="5" valign="top">original_condition</th>
      <th rowspan="5" valign="top">cooling</th>
      <th rowspan="5" valign="top">PRE_TEK49</th>
      <th>2010</th>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>2011</th>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>2012</th>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>2013</th>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>2014</th>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">university</th>
      <th rowspan="5" valign="top">small_measure</th>
      <th rowspan="5" valign="top">lighting</th>
      <th rowspan="5" valign="top">TEK97</th>
      <th>2046</th>
      <td>267379.867</td>
      <td>9.250</td>
      <td>2473270.696</td>
    </tr>
    <tr>
      <th>2047</th>
      <td>262714.941</td>
      <td>9.204</td>
      <td>2417969.416</td>
    </tr>
    <tr>
      <th>2048</th>
      <td>258050.016</td>
      <td>9.158</td>
      <td>2363159.317</td>
    </tr>
    <tr>
      <th>2049</th>
      <td>253385.091</td>
      <td>9.112</td>
      <td>2308836.869</td>
    </tr>
    <tr>
      <th>2050</th>
      <td>248720.165</td>
      <td>9.066</td>
      <td>2254998.567</td>
    </tr>
  </tbody>
</table>
</div>




```python

```

## Load energy_requirement into df


```python

```


```python

```

## Load tekandeler


```python
#ta_df = pd.read_excel('input/Innfyrt_energi_2019_v7.xlsx')
ta_df = pd.read_excel('input/Oppvarmingsandeler_fordelt_TEK_leilighet (2).xlsx')



ta_df = ta_df.rename(columns={'Bygningskategori': 'building_category',
                              'Formål': 'purpose',
                              'TEK_andeler': 'tek_share',
                              'TEK': 'tek'})
ta_df.loc[:, 'building_category'] = ta_df.building_category.apply(lambda x: BuildingCategory.from_string(x))
ta_df.tek = ta_df['tek'].str.upper()
ta_df = ta_df.drop(columns=['Unnamed: 0'])
ta_df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>building_category</th>
      <th>tek</th>
      <th>Oppvarmingstyper</th>
      <th>tek_share</th>
      <th>Grunnlast</th>
      <th>Spisslast</th>
      <th>Ekstralast</th>
      <th>Ekstralast andel</th>
      <th>Grunnlast andel</th>
      <th>Spisslast andel</th>
      <th>Grunnlast virkningsgrad</th>
      <th>Spisslast virkningsgrad</th>
      <th>Ekstralast virkningsgrad</th>
      <th>Tappevann</th>
      <th>Tappevann virkningsgrad</th>
      <th>Spesifikt elforbruk</th>
      <th>Kjoling virkningsgrad</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>apartment_block</td>
      <td>TEK07</td>
      <td>Electricity</td>
      <td>0.000</td>
      <td>Electricity</td>
      <td>Ingen</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>1</td>
      <td>Electricity</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>1</th>
      <td>retail</td>
      <td>TEK97</td>
      <td>Electricity</td>
      <td>0.082</td>
      <td>Electricity</td>
      <td>Ingen</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>1</td>
      <td>Electricity</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2</th>
      <td>retail</td>
      <td>PRE_TEK49</td>
      <td>Electricity</td>
      <td>0.076</td>
      <td>Electricity</td>
      <td>Ingen</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>1</td>
      <td>Electricity</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>3</th>
      <td>sports</td>
      <td>TEK07</td>
      <td>Electricity</td>
      <td>0.061</td>
      <td>Electricity</td>
      <td>Ingen</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>1</td>
      <td>Electricity</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>sports</td>
      <td>TEK10</td>
      <td>Electricity</td>
      <td>0.089</td>
      <td>Electricity</td>
      <td>Ingen</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>1</td>
      <td>Electricity</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>773</th>
      <td>sports</td>
      <td>TEK87</td>
      <td>Gas</td>
      <td>0.020</td>
      <td>Gas</td>
      <td>Ingen</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>0.960</td>
      <td>1.000</td>
      <td>1</td>
      <td>Gas</td>
      <td>0.960</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>774</th>
      <td>house</td>
      <td>TEK87</td>
      <td>Gas</td>
      <td>0.003</td>
      <td>Gas</td>
      <td>Ingen</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>0.960</td>
      <td>1.000</td>
      <td>1</td>
      <td>Gas</td>
      <td>0.960</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>775</th>
      <td>sports</td>
      <td>TEK69</td>
      <td>Gas</td>
      <td>0.012</td>
      <td>Gas</td>
      <td>Ingen</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>0.960</td>
      <td>1.000</td>
      <td>1</td>
      <td>Gas</td>
      <td>0.960</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>776</th>
      <td>school</td>
      <td>TEK69</td>
      <td>Gas</td>
      <td>0.004</td>
      <td>Gas</td>
      <td>Ingen</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>0.960</td>
      <td>1.000</td>
      <td>1</td>
      <td>Gas</td>
      <td>0.960</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>777</th>
      <td>school</td>
      <td>TEK10</td>
      <td>Gas</td>
      <td>0.038</td>
      <td>Gas</td>
      <td>Ingen</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>0.960</td>
      <td>1.000</td>
      <td>1</td>
      <td>Gas</td>
      <td>0.960</td>
      <td>1</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>




```python



```


```python
ta_df = ta_df.set_index(['building_category', 'tek']).sort_index()
#ta_df = ta_df[['tek_share', 'Grunnlast andel', 'Grunnlast virkningsgrad', 'Spisslast andel', 'Spisslast virkningsgrad']]

ta_df= ta_df.drop(columns=['Unnamed: 0'], errors='ignore')
ta_df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th>Oppvarmingstyper</th>
      <th>tek_share</th>
      <th>Grunnlast</th>
      <th>Spisslast</th>
      <th>Ekstralast</th>
      <th>Ekstralast andel</th>
      <th>Grunnlast andel</th>
      <th>Spisslast andel</th>
      <th>Grunnlast virkningsgrad</th>
      <th>Spisslast virkningsgrad</th>
      <th>Ekstralast virkningsgrad</th>
      <th>Tappevann</th>
      <th>Tappevann virkningsgrad</th>
      <th>Spesifikt elforbruk</th>
      <th>Kjoling virkningsgrad</th>
    </tr>
    <tr>
      <th>building_category</th>
      <th>tek</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">apartment_block</th>
      <th>PRE_TEK49</th>
      <td>Electricity</td>
      <td>0.084</td>
      <td>Electricity</td>
      <td>Ingen</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>1</td>
      <td>Electricity</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>PRE_TEK49</th>
      <td>Electricity</td>
      <td>0.304</td>
      <td>Electricity</td>
      <td>Ingen</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>1</td>
      <td>Electricity</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>PRE_TEK49</th>
      <td>Electricity - Bio</td>
      <td>0.380</td>
      <td>Electricity</td>
      <td>Bio</td>
      <td>Electricity</td>
      <td>0.150</td>
      <td>0.700</td>
      <td>0.150</td>
      <td>1.000</td>
      <td>0.650</td>
      <td>1</td>
      <td>Electricity</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>PRE_TEK49</th>
      <td>DH</td>
      <td>0.103</td>
      <td>DH</td>
      <td>Ingen</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>0.990</td>
      <td>1.000</td>
      <td>1</td>
      <td>DH</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>PRE_TEK49</th>
      <td>DH - Bio</td>
      <td>0.021</td>
      <td>DH</td>
      <td>Bio</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>0.950</td>
      <td>0.050</td>
      <td>0.990</td>
      <td>0.650</td>
      <td>1</td>
      <td>DH</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">university</th>
      <th>TEK97</th>
      <td>Electricity - Bio</td>
      <td>0.005</td>
      <td>Electricity</td>
      <td>Bio</td>
      <td>Electricity</td>
      <td>0.150</td>
      <td>0.700</td>
      <td>0.150</td>
      <td>1.000</td>
      <td>0.650</td>
      <td>1</td>
      <td>Electricity</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>TEK97</th>
      <td>DH</td>
      <td>0.869</td>
      <td>DH</td>
      <td>Ingen</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>0.990</td>
      <td>1.000</td>
      <td>1</td>
      <td>DH</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>TEK97</th>
      <td>Electric boiler</td>
      <td>0.011</td>
      <td>Electric boiler</td>
      <td>Ingen</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>0.980</td>
      <td>1.000</td>
      <td>1</td>
      <td>Electric boiler</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>TEK97</th>
      <td>HP Central heating</td>
      <td>0.011</td>
      <td>HP Central heating</td>
      <td>Electric boiler</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>0.850</td>
      <td>0.150</td>
      <td>3.000</td>
      <td>0.980</td>
      <td>1</td>
      <td>HP Central heating</td>
      <td>3.000</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>TEK97</th>
      <td>Gas</td>
      <td>0.017</td>
      <td>Gas</td>
      <td>Ingen</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>0.960</td>
      <td>1.000</td>
      <td>1</td>
      <td>Gas</td>
      <td>0.960</td>
      <td>1</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>




```python
ta_df.loc[('kindergarten', 'TEK07')]
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th>Oppvarmingstyper</th>
      <th>tek_share</th>
      <th>Grunnlast</th>
      <th>Spisslast</th>
      <th>Ekstralast</th>
      <th>Ekstralast andel</th>
      <th>Grunnlast andel</th>
      <th>Spisslast andel</th>
      <th>Grunnlast virkningsgrad</th>
      <th>Spisslast virkningsgrad</th>
      <th>Ekstralast virkningsgrad</th>
      <th>Tappevann</th>
      <th>Tappevann virkningsgrad</th>
      <th>Spesifikt elforbruk</th>
      <th>Kjoling virkningsgrad</th>
    </tr>
    <tr>
      <th>building_category</th>
      <th>tek</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="6" valign="top">kindergarten</th>
      <th>TEK07</th>
      <td>Electricity</td>
      <td>0.598</td>
      <td>Electricity</td>
      <td>Ingen</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>1</td>
      <td>Electricity</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>TEK07</th>
      <td>Electricity - Bio</td>
      <td>0.004</td>
      <td>Electricity</td>
      <td>Bio</td>
      <td>Electricity</td>
      <td>0.150</td>
      <td>0.700</td>
      <td>0.150</td>
      <td>1.000</td>
      <td>0.650</td>
      <td>1</td>
      <td>Electricity</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>TEK07</th>
      <td>DH</td>
      <td>0.280</td>
      <td>DH</td>
      <td>Ingen</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>0.990</td>
      <td>1.000</td>
      <td>1</td>
      <td>DH</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>TEK07</th>
      <td>Electric boiler</td>
      <td>0.011</td>
      <td>Electric boiler</td>
      <td>Ingen</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>0.980</td>
      <td>1.000</td>
      <td>1</td>
      <td>Electric boiler</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>TEK07</th>
      <td>HP Central heating</td>
      <td>0.095</td>
      <td>HP Central heating</td>
      <td>Electric boiler</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>0.850</td>
      <td>0.150</td>
      <td>3.000</td>
      <td>0.980</td>
      <td>1</td>
      <td>HP Central heating</td>
      <td>3.000</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>TEK07</th>
      <td>HP Central heating</td>
      <td>0.011</td>
      <td>HP Central heating</td>
      <td>Electric boiler</td>
      <td>Ingen</td>
      <td>0.000</td>
      <td>0.850</td>
      <td>0.150</td>
      <td>3.000</td>
      <td>0.980</td>
      <td>1</td>
      <td>HP Central heating</td>
      <td>3.000</td>
      <td>1</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>




```python

```



### energy requirement by tek_share


```python
#ts_df = ta_df.copy().reset_index()
#df2 = df.reset_index().set_index(['building_category', 'building_condition', 'purpose', 'tek'])
#ts_df.loc[:, 'energy_requirement'] = \
#df2.loc[:, 'energy_requirement']


#ts_df
```


```python
d2 = df.reset_index().merge(ta_df.reset_index(), left_on=['building_category', 'tek'],
                            right_on=['building_category', 'tek'])[
    ['building_category', 'building_condition', 'purpose', 'tek', 'year', 'kwh_m2', 'm2', 'energy_requirement', 'Oppvarmingstyper', 'tek_share', 'Grunnlast andel', 'Grunnlast virkningsgrad', 'Spisslast andel', 'Spisslast virkningsgrad', 'Ekstralast andel', 'Ekstralast virkningsgrad', 'Tappevann virkningsgrad', 'Spesifikt elforbruk', 'Kjoling virkningsgrad']] # ,'Innfyrt_energi_kWh','Innfyrt_energi_GWh','Energibehov_samlet_GWh']]

d2 = d2.set_index(['building_category', 'building_condition', 'purpose', 'tek', 'year']).sort_index()
d2
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th>kwh_m2</th>
      <th>m2</th>
      <th>energy_requirement</th>
      <th>Oppvarmingstyper</th>
      <th>tek_share</th>
      <th>Grunnlast andel</th>
      <th>Grunnlast virkningsgrad</th>
      <th>Spisslast andel</th>
      <th>Spisslast virkningsgrad</th>
      <th>Ekstralast andel</th>
      <th>Ekstralast virkningsgrad</th>
      <th>Tappevann virkningsgrad</th>
      <th>Spesifikt elforbruk</th>
      <th>Kjoling virkningsgrad</th>
    </tr>
    <tr>
      <th>building_category</th>
      <th>building_condition</th>
      <th>purpose</th>
      <th>tek</th>
      <th>year</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">apartment_block</th>
      <th rowspan="5" valign="top">original_condition</th>
      <th rowspan="5" valign="top">cooling</th>
      <th rowspan="5" valign="top">PRE_TEK49</th>
      <th>2010</th>
      <td>0.000</td>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>Electricity</td>
      <td>0.084</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2010</th>
      <td>0.000</td>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>Electricity</td>
      <td>0.304</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2010</th>
      <td>0.000</td>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>Electricity - Bio</td>
      <td>0.380</td>
      <td>0.700</td>
      <td>1.000</td>
      <td>0.150</td>
      <td>0.650</td>
      <td>0.150</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2010</th>
      <td>0.000</td>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>DH</td>
      <td>0.103</td>
      <td>1.000</td>
      <td>0.990</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2010</th>
      <td>0.000</td>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>DH - Bio</td>
      <td>0.021</td>
      <td>0.950</td>
      <td>0.990</td>
      <td>0.050</td>
      <td>0.650</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">university</th>
      <th rowspan="5" valign="top">small_measure</th>
      <th rowspan="5" valign="top">lighting</th>
      <th rowspan="5" valign="top">TEK97</th>
      <th>2050</th>
      <td>9.066</td>
      <td>248720.165</td>
      <td>2254998.567</td>
      <td>Electricity - Bio</td>
      <td>0.005</td>
      <td>0.700</td>
      <td>1.000</td>
      <td>0.150</td>
      <td>0.650</td>
      <td>0.150</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2050</th>
      <td>9.066</td>
      <td>248720.165</td>
      <td>2254998.567</td>
      <td>DH</td>
      <td>0.869</td>
      <td>1.000</td>
      <td>0.990</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2050</th>
      <td>9.066</td>
      <td>248720.165</td>
      <td>2254998.567</td>
      <td>Electric boiler</td>
      <td>0.011</td>
      <td>1.000</td>
      <td>0.980</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2050</th>
      <td>9.066</td>
      <td>248720.165</td>
      <td>2254998.567</td>
      <td>HP Central heating</td>
      <td>0.011</td>
      <td>0.850</td>
      <td>3.000</td>
      <td>0.150</td>
      <td>0.980</td>
      <td>0.000</td>
      <td>1</td>
      <td>3.000</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2050</th>
      <td>9.066</td>
      <td>248720.165</td>
      <td>2254998.567</td>
      <td>Gas</td>
      <td>0.017</td>
      <td>1.000</td>
      <td>0.960</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.960</td>
      <td>1</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>




```python

```


```python
d2.loc[(['kindergarten'], ['original_condition'], ['electrical_equipment', ], ['TEK07'], [2019])]

```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th>kwh_m2</th>
      <th>m2</th>
      <th>energy_requirement</th>
      <th>Oppvarmingstyper</th>
      <th>tek_share</th>
      <th>Grunnlast andel</th>
      <th>Grunnlast virkningsgrad</th>
      <th>Spisslast andel</th>
      <th>Spisslast virkningsgrad</th>
      <th>Ekstralast andel</th>
      <th>Ekstralast virkningsgrad</th>
      <th>Tappevann virkningsgrad</th>
      <th>Spesifikt elforbruk</th>
      <th>Kjoling virkningsgrad</th>
    </tr>
    <tr>
      <th>building_category</th>
      <th>building_condition</th>
      <th>purpose</th>
      <th>tek</th>
      <th>year</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="6" valign="top">kindergarten</th>
      <th rowspan="6" valign="top">original_condition</th>
      <th rowspan="6" valign="top">electrical_equipment</th>
      <th rowspan="6" valign="top">TEK07</th>
      <th>2019</th>
      <td>5.220</td>
      <td>273704.344</td>
      <td>1428736.674</td>
      <td>Electricity</td>
      <td>0.598</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2019</th>
      <td>5.220</td>
      <td>273704.344</td>
      <td>1428736.674</td>
      <td>Electricity - Bio</td>
      <td>0.004</td>
      <td>0.700</td>
      <td>1.000</td>
      <td>0.150</td>
      <td>0.650</td>
      <td>0.150</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2019</th>
      <td>5.220</td>
      <td>273704.344</td>
      <td>1428736.674</td>
      <td>DH</td>
      <td>0.280</td>
      <td>1.000</td>
      <td>0.990</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2019</th>
      <td>5.220</td>
      <td>273704.344</td>
      <td>1428736.674</td>
      <td>Electric boiler</td>
      <td>0.011</td>
      <td>1.000</td>
      <td>0.980</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2019</th>
      <td>5.220</td>
      <td>273704.344</td>
      <td>1428736.674</td>
      <td>HP Central heating</td>
      <td>0.095</td>
      <td>0.850</td>
      <td>3.000</td>
      <td>0.150</td>
      <td>0.980</td>
      <td>0.000</td>
      <td>1</td>
      <td>3.000</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2019</th>
      <td>5.220</td>
      <td>273704.344</td>
      <td>1428736.674</td>
      <td>HP Central heating</td>
      <td>0.011</td>
      <td>0.850</td>
      <td>3.000</td>
      <td>0.150</td>
      <td>0.980</td>
      <td>0.000</td>
      <td>1</td>
      <td>3.000</td>
      <td>1</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>




```python
d2['eq_ts'] = d2.energy_requirement * d2.tek_share
d2.loc[(BuildingCategory.KINDERGARTEN, slice(None), slice(None), 'TEK07', 2019)]


```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th>kwh_m2</th>
      <th>m2</th>
      <th>energy_requirement</th>
      <th>Oppvarmingstyper</th>
      <th>tek_share</th>
      <th>Grunnlast andel</th>
      <th>Grunnlast virkningsgrad</th>
      <th>Spisslast andel</th>
      <th>Spisslast virkningsgrad</th>
      <th>Ekstralast andel</th>
      <th>Ekstralast virkningsgrad</th>
      <th>Tappevann virkningsgrad</th>
      <th>Spesifikt elforbruk</th>
      <th>Kjoling virkningsgrad</th>
      <th>eq_ts</th>
    </tr>
    <tr>
      <th>building_condition</th>
      <th>purpose</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">original_condition</th>
      <th>cooling</th>
      <td>0.000</td>
      <td>273704.344</td>
      <td>0.000</td>
      <td>Electricity</td>
      <td>0.598</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>cooling</th>
      <td>0.000</td>
      <td>273704.344</td>
      <td>0.000</td>
      <td>Electricity - Bio</td>
      <td>0.004</td>
      <td>0.700</td>
      <td>1.000</td>
      <td>0.150</td>
      <td>0.650</td>
      <td>0.150</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>cooling</th>
      <td>0.000</td>
      <td>273704.344</td>
      <td>0.000</td>
      <td>DH</td>
      <td>0.280</td>
      <td>1.000</td>
      <td>0.990</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>cooling</th>
      <td>0.000</td>
      <td>273704.344</td>
      <td>0.000</td>
      <td>Electric boiler</td>
      <td>0.011</td>
      <td>1.000</td>
      <td>0.980</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>cooling</th>
      <td>0.000</td>
      <td>273704.344</td>
      <td>0.000</td>
      <td>HP Central heating</td>
      <td>0.095</td>
      <td>0.850</td>
      <td>3.000</td>
      <td>0.150</td>
      <td>0.980</td>
      <td>0.000</td>
      <td>1</td>
      <td>3.000</td>
      <td>1</td>
      <td>4</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">small_measure</th>
      <th>lighting</th>
      <td>19.836</td>
      <td>11280.656</td>
      <td>223763.097</td>
      <td>Electricity - Bio</td>
      <td>0.004</td>
      <td>0.700</td>
      <td>1.000</td>
      <td>0.150</td>
      <td>0.650</td>
      <td>0.150</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
      <td>832.170</td>
    </tr>
    <tr>
      <th>lighting</th>
      <td>19.836</td>
      <td>11280.656</td>
      <td>223763.097</td>
      <td>DH</td>
      <td>0.280</td>
      <td>1.000</td>
      <td>0.990</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
      <td>62762.920</td>
    </tr>
    <tr>
      <th>lighting</th>
      <td>19.836</td>
      <td>11280.656</td>
      <td>223763.097</td>
      <td>Electric boiler</td>
      <td>0.011</td>
      <td>1.000</td>
      <td>0.980</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
      <td>2517.108</td>
    </tr>
    <tr>
      <th>lighting</th>
      <td>19.836</td>
      <td>11280.656</td>
      <td>223763.097</td>
      <td>HP Central heating</td>
      <td>0.095</td>
      <td>0.850</td>
      <td>3.000</td>
      <td>0.150</td>
      <td>0.980</td>
      <td>0.000</td>
      <td>1</td>
      <td>3.000</td>
      <td>1</td>
      <td>4</td>
      <td>21228.574</td>
    </tr>
    <tr>
      <th>lighting</th>
      <td>19.836</td>
      <td>11280.656</td>
      <td>223763.097</td>
      <td>HP Central heating</td>
      <td>0.011</td>
      <td>0.850</td>
      <td>3.000</td>
      <td>0.150</td>
      <td>0.980</td>
      <td>0.000</td>
      <td>1</td>
      <td>3.000</td>
      <td>1</td>
      <td>4</td>
      <td>2517.108</td>
    </tr>
  </tbody>
</table>
</div>



## Legge inn grunnlast, spisslast og ekstralast


```python
d2.loc[:, ['RV_GL', 'RV_SL', 'RV_EL', 'DHW_TV', 'CL_KV', 'O_SV']] = 0.0

heating_rv_slice = (slice(None), slice(None), 'heating_rv', slice(None), slice(None))
d2.loc[heating_rv_slice, 'RV_GL'] = (d2.loc[heating_rv_slice, 'eq_ts'] * d2.loc[heating_rv_slice, 'Grunnlast andel'] / d2.loc[heating_rv_slice, 'Grunnlast virkningsgrad'])
d2.loc[heating_rv_slice, 'RV_SL'] = (d2.loc[heating_rv_slice, 'eq_ts'] * d2.loc[heating_rv_slice, 'Spisslast andel'] / d2.loc[heating_rv_slice, 'Spisslast virkningsgrad'])
d2.loc[heating_rv_slice, 'RV_EL'] = (d2.loc[heating_rv_slice, 'eq_ts'] * d2.loc[heating_rv_slice, 'Ekstralast andel'] / d2.loc[heating_rv_slice, 'Ekstralast virkningsgrad'])

heating_dhw_slice = (slice(None), slice(None), 'heating_dhw', slice(None), slice(None))
d2.loc[heating_dhw_slice, 'DHW_TV'] = d2.loc[heating_dhw_slice, 'eq_ts'] / d2.loc[heating_dhw_slice, 'Tappevann virkningsgrad']

cooling_slice = (slice(None), slice(None), 'cooling', slice(None), slice(None))
d2.loc[cooling_slice, 'CL_KV'] = d2.loc[cooling_slice, 'eq_ts'] / d2.loc[cooling_slice, 'Kjoling virkningsgrad']


other_slice = (slice(None), slice(None), [e for e in EnergyPurpose if e not in ('heating_rv', 'heating_dhw', 'cooling')], slice(None), slice(None))
d2.loc[other_slice, 'O_SV'] = d2.loc[other_slice, 'eq_ts'] / d2.loc[other_slice, 'Spesifikt elforbruk']

d2.loc[:, 'sums'] = d2.loc[:, ['RV_GL', 'RV_SL', 'RV_EL', 'DHW_TV', 'CL_KV', 'O_SV']].sum(axis=1)

d2
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th>kwh_m2</th>
      <th>m2</th>
      <th>energy_requirement</th>
      <th>Oppvarmingstyper</th>
      <th>tek_share</th>
      <th>Grunnlast andel</th>
      <th>Grunnlast virkningsgrad</th>
      <th>Spisslast andel</th>
      <th>Spisslast virkningsgrad</th>
      <th>Ekstralast andel</th>
      <th>Ekstralast virkningsgrad</th>
      <th>Tappevann virkningsgrad</th>
      <th>Spesifikt elforbruk</th>
      <th>Kjoling virkningsgrad</th>
      <th>eq_ts</th>
      <th>RV_GL</th>
      <th>RV_SL</th>
      <th>RV_EL</th>
      <th>DHW_TV</th>
      <th>CL_KV</th>
      <th>O_SV</th>
      <th>sums</th>
    </tr>
    <tr>
      <th>building_category</th>
      <th>building_condition</th>
      <th>purpose</th>
      <th>tek</th>
      <th>year</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">apartment_block</th>
      <th rowspan="5" valign="top">original_condition</th>
      <th rowspan="5" valign="top">cooling</th>
      <th rowspan="5" valign="top">PRE_TEK49</th>
      <th>2010</th>
      <td>0.000</td>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>Electricity</td>
      <td>0.084</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>2010</th>
      <td>0.000</td>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>Electricity</td>
      <td>0.304</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>2010</th>
      <td>0.000</td>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>Electricity - Bio</td>
      <td>0.380</td>
      <td>0.700</td>
      <td>1.000</td>
      <td>0.150</td>
      <td>0.650</td>
      <td>0.150</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>2010</th>
      <td>0.000</td>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>DH</td>
      <td>0.103</td>
      <td>1.000</td>
      <td>0.990</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>2010</th>
      <td>0.000</td>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>DH - Bio</td>
      <td>0.021</td>
      <td>0.950</td>
      <td>0.990</td>
      <td>0.050</td>
      <td>0.650</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">university</th>
      <th rowspan="5" valign="top">small_measure</th>
      <th rowspan="5" valign="top">lighting</th>
      <th rowspan="5" valign="top">TEK97</th>
      <th>2050</th>
      <td>9.066</td>
      <td>248720.165</td>
      <td>2254998.567</td>
      <td>Electricity - Bio</td>
      <td>0.005</td>
      <td>0.700</td>
      <td>1.000</td>
      <td>0.150</td>
      <td>0.650</td>
      <td>0.150</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
      <td>10366.986</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>10366.986</td>
      <td>10366.986</td>
    </tr>
    <tr>
      <th>2050</th>
      <td>9.066</td>
      <td>248720.165</td>
      <td>2254998.567</td>
      <td>DH</td>
      <td>0.869</td>
      <td>1.000</td>
      <td>0.990</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
      <td>1959114.755</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>1959114.755</td>
      <td>1959114.755</td>
    </tr>
    <tr>
      <th>2050</th>
      <td>9.066</td>
      <td>248720.165</td>
      <td>2254998.567</td>
      <td>Electric boiler</td>
      <td>0.011</td>
      <td>1.000</td>
      <td>0.980</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
      <td>24182.812</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>24182.812</td>
      <td>24182.812</td>
    </tr>
    <tr>
      <th>2050</th>
      <td>9.066</td>
      <td>248720.165</td>
      <td>2254998.567</td>
      <td>HP Central heating</td>
      <td>0.011</td>
      <td>0.850</td>
      <td>3.000</td>
      <td>0.150</td>
      <td>0.980</td>
      <td>0.000</td>
      <td>1</td>
      <td>3.000</td>
      <td>1</td>
      <td>4</td>
      <td>24182.812</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>24182.812</td>
      <td>24182.812</td>
    </tr>
    <tr>
      <th>2050</th>
      <td>9.066</td>
      <td>248720.165</td>
      <td>2254998.567</td>
      <td>Gas</td>
      <td>0.017</td>
      <td>1.000</td>
      <td>0.960</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.960</td>
      <td>1</td>
      <td>4</td>
      <td>37517.642</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>37517.642</td>
      <td>37517.642</td>
    </tr>
  </tbody>
</table>
</div>




```python

```


```python
d2.loc[:, 'gsums'] = d2.loc[:, 'sums'] / 10**6
d2[['Oppvarmingstyper', 'kwh_m2','m2', 'eq_ts', 'gsums', 'RV_GL', 'RV_SL', 'RV_EL', 'DHW_TV', 'CL_KV', 'O_SV']]
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th>Oppvarmingstyper</th>
      <th>kwh_m2</th>
      <th>m2</th>
      <th>eq_ts</th>
      <th>gsums</th>
      <th>RV_GL</th>
      <th>RV_SL</th>
      <th>RV_EL</th>
      <th>DHW_TV</th>
      <th>CL_KV</th>
      <th>O_SV</th>
    </tr>
    <tr>
      <th>building_category</th>
      <th>building_condition</th>
      <th>purpose</th>
      <th>tek</th>
      <th>year</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">apartment_block</th>
      <th rowspan="5" valign="top">original_condition</th>
      <th rowspan="5" valign="top">cooling</th>
      <th rowspan="5" valign="top">PRE_TEK49</th>
      <th>2010</th>
      <td>Electricity</td>
      <td>0.000</td>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>2010</th>
      <td>Electricity</td>
      <td>0.000</td>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>2010</th>
      <td>Electricity - Bio</td>
      <td>0.000</td>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>2010</th>
      <td>DH</td>
      <td>0.000</td>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>2010</th>
      <td>DH - Bio</td>
      <td>0.000</td>
      <td>1144424.500</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">university</th>
      <th rowspan="5" valign="top">small_measure</th>
      <th rowspan="5" valign="top">lighting</th>
      <th rowspan="5" valign="top">TEK97</th>
      <th>2050</th>
      <td>Electricity - Bio</td>
      <td>9.066</td>
      <td>248720.165</td>
      <td>10366.986</td>
      <td>0.010</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>10366.986</td>
    </tr>
    <tr>
      <th>2050</th>
      <td>DH</td>
      <td>9.066</td>
      <td>248720.165</td>
      <td>1959114.755</td>
      <td>1.959</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>1959114.755</td>
    </tr>
    <tr>
      <th>2050</th>
      <td>Electric boiler</td>
      <td>9.066</td>
      <td>248720.165</td>
      <td>24182.812</td>
      <td>0.024</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>24182.812</td>
    </tr>
    <tr>
      <th>2050</th>
      <td>HP Central heating</td>
      <td>9.066</td>
      <td>248720.165</td>
      <td>24182.812</td>
      <td>0.024</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>24182.812</td>
    </tr>
    <tr>
      <th>2050</th>
      <td>Gas</td>
      <td>9.066</td>
      <td>248720.165</td>
      <td>37517.642</td>
      <td>0.038</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>37517.642</td>
    </tr>
  </tbody>
</table>
</div>



## Filtrer TEK07, 2019


```python
d2.loc[('kindergarten', slice(None), slice(None), 'TEK07', 2019)]
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th>kwh_m2</th>
      <th>m2</th>
      <th>energy_requirement</th>
      <th>Oppvarmingstyper</th>
      <th>tek_share</th>
      <th>Grunnlast andel</th>
      <th>Grunnlast virkningsgrad</th>
      <th>Spisslast andel</th>
      <th>Spisslast virkningsgrad</th>
      <th>Ekstralast andel</th>
      <th>Ekstralast virkningsgrad</th>
      <th>Tappevann virkningsgrad</th>
      <th>Spesifikt elforbruk</th>
      <th>Kjoling virkningsgrad</th>
      <th>eq_ts</th>
      <th>RV_GL</th>
      <th>RV_SL</th>
      <th>RV_EL</th>
      <th>DHW_TV</th>
      <th>CL_KV</th>
      <th>O_SV</th>
      <th>sums</th>
      <th>gsums</th>
    </tr>
    <tr>
      <th>building_condition</th>
      <th>purpose</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">original_condition</th>
      <th>cooling</th>
      <td>0.000</td>
      <td>273704.344</td>
      <td>0.000</td>
      <td>Electricity</td>
      <td>0.598</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>cooling</th>
      <td>0.000</td>
      <td>273704.344</td>
      <td>0.000</td>
      <td>Electricity - Bio</td>
      <td>0.004</td>
      <td>0.700</td>
      <td>1.000</td>
      <td>0.150</td>
      <td>0.650</td>
      <td>0.150</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>cooling</th>
      <td>0.000</td>
      <td>273704.344</td>
      <td>0.000</td>
      <td>DH</td>
      <td>0.280</td>
      <td>1.000</td>
      <td>0.990</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>cooling</th>
      <td>0.000</td>
      <td>273704.344</td>
      <td>0.000</td>
      <td>Electric boiler</td>
      <td>0.011</td>
      <td>1.000</td>
      <td>0.980</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>cooling</th>
      <td>0.000</td>
      <td>273704.344</td>
      <td>0.000</td>
      <td>HP Central heating</td>
      <td>0.095</td>
      <td>0.850</td>
      <td>3.000</td>
      <td>0.150</td>
      <td>0.980</td>
      <td>0.000</td>
      <td>1</td>
      <td>3.000</td>
      <td>1</td>
      <td>4</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">small_measure</th>
      <th>lighting</th>
      <td>19.836</td>
      <td>11280.656</td>
      <td>223763.097</td>
      <td>Electricity - Bio</td>
      <td>0.004</td>
      <td>0.700</td>
      <td>1.000</td>
      <td>0.150</td>
      <td>0.650</td>
      <td>0.150</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
      <td>832.170</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>832.170</td>
      <td>832.170</td>
      <td>0.001</td>
    </tr>
    <tr>
      <th>lighting</th>
      <td>19.836</td>
      <td>11280.656</td>
      <td>223763.097</td>
      <td>DH</td>
      <td>0.280</td>
      <td>1.000</td>
      <td>0.990</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
      <td>62762.920</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>62762.920</td>
      <td>62762.920</td>
      <td>0.063</td>
    </tr>
    <tr>
      <th>lighting</th>
      <td>19.836</td>
      <td>11280.656</td>
      <td>223763.097</td>
      <td>Electric boiler</td>
      <td>0.011</td>
      <td>1.000</td>
      <td>0.980</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
      <td>2517.108</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>2517.108</td>
      <td>2517.108</td>
      <td>0.003</td>
    </tr>
    <tr>
      <th>lighting</th>
      <td>19.836</td>
      <td>11280.656</td>
      <td>223763.097</td>
      <td>HP Central heating</td>
      <td>0.095</td>
      <td>0.850</td>
      <td>3.000</td>
      <td>0.150</td>
      <td>0.980</td>
      <td>0.000</td>
      <td>1</td>
      <td>3.000</td>
      <td>1</td>
      <td>4</td>
      <td>21228.574</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>21228.574</td>
      <td>21228.574</td>
      <td>0.021</td>
    </tr>
    <tr>
      <th>lighting</th>
      <td>19.836</td>
      <td>11280.656</td>
      <td>223763.097</td>
      <td>HP Central heating</td>
      <td>0.011</td>
      <td>0.850</td>
      <td>3.000</td>
      <td>0.150</td>
      <td>0.980</td>
      <td>0.000</td>
      <td>1</td>
      <td>3.000</td>
      <td>1</td>
      <td>4</td>
      <td>2517.108</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>2517.108</td>
      <td>2517.108</td>
      <td>0.003</td>
    </tr>
  </tbody>
</table>
</div>



### Sum TEK07, 2019


```python
d2.loc[('kindergarten', slice(None), slice(None), 'TEK07', 2019)].sum()['sums']
```




    np.float64(40926199.66228827)




```python
47_715_821.5003
```




    47715821.5003




```python
42_851_519.52
41_318_635.84
```




    41318635.84




```python
pd.set_option('display.float_format', '{:.3f}'.format)

d2.loc[(slice(None), slice(None), ['heating_rv', 'heating_dhw', 'lighting', 'cooling', 'fans_and_pumps', 'electrical_equipment'], ['TEK07'], [2019])]
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th>kwh_m2</th>
      <th>m2</th>
      <th>energy_requirement</th>
      <th>Oppvarmingstyper</th>
      <th>tek_share</th>
      <th>Grunnlast andel</th>
      <th>Grunnlast virkningsgrad</th>
      <th>Spisslast andel</th>
      <th>Spisslast virkningsgrad</th>
      <th>Ekstralast andel</th>
      <th>Ekstralast virkningsgrad</th>
      <th>Tappevann virkningsgrad</th>
      <th>Spesifikt elforbruk</th>
      <th>Kjoling virkningsgrad</th>
      <th>eq_ts</th>
      <th>RV_GL</th>
      <th>RV_SL</th>
      <th>RV_EL</th>
      <th>DHW_TV</th>
      <th>CL_KV</th>
      <th>O_SV</th>
      <th>sums</th>
      <th>gsums</th>
    </tr>
    <tr>
      <th>building_category</th>
      <th>building_condition</th>
      <th>purpose</th>
      <th>tek</th>
      <th>year</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">apartment_block</th>
      <th rowspan="5" valign="top">original_condition</th>
      <th rowspan="5" valign="top">heating_rv</th>
      <th rowspan="5" valign="top">TEK07</th>
      <th>2019</th>
      <td>39.528</td>
      <td>3706372.260</td>
      <td>146505282.702</td>
      <td>Electricity</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>2019</th>
      <td>39.528</td>
      <td>3706372.260</td>
      <td>146505282.702</td>
      <td>Electricity - Bio</td>
      <td>0.063</td>
      <td>0.700</td>
      <td>1.000</td>
      <td>0.150</td>
      <td>0.650</td>
      <td>0.150</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
      <td>9180584.933</td>
      <td>6426409.453</td>
      <td>2118596.523</td>
      <td>1377087.740</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>9922093.717</td>
      <td>9.922</td>
    </tr>
    <tr>
      <th>2019</th>
      <td>39.528</td>
      <td>3706372.260</td>
      <td>146505282.702</td>
      <td>DH</td>
      <td>0.332</td>
      <td>1.000</td>
      <td>0.990</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
      <td>48590967.988</td>
      <td>49081785.846</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>49081785.846</td>
      <td>49.082</td>
    </tr>
    <tr>
      <th>2019</th>
      <td>39.528</td>
      <td>3706372.260</td>
      <td>146505282.702</td>
      <td>DH - Bio</td>
      <td>0.003</td>
      <td>0.950</td>
      <td>0.990</td>
      <td>0.050</td>
      <td>0.650</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
      <td>484329.961</td>
      <td>464761.074</td>
      <td>37256.151</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>502017.225</td>
      <td>0.502</td>
    </tr>
    <tr>
      <th>2019</th>
      <td>39.528</td>
      <td>3706372.260</td>
      <td>146505282.702</td>
      <td>Electric boiler</td>
      <td>0.003</td>
      <td>1.000</td>
      <td>0.980</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.980</td>
      <td>1</td>
      <td>4</td>
      <td>390840.192</td>
      <td>398816.522</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>398816.522</td>
      <td>0.399</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>storage_repairs</th>
      <th>small_measure</th>
      <th>electrical_equipment</th>
      <th>TEK07</th>
      <th>2019</th>
      <td>23.490</td>
      <td>35085.671</td>
      <td>824162.422</td>
      <td>Gas</td>
      <td>0.232</td>
      <td>1.000</td>
      <td>0.960</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.960</td>
      <td>1</td>
      <td>4</td>
      <td>191247.335</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>191247.335</td>
      <td>191247.335</td>
      <td>0.191</td>
    </tr>
    <tr>
      <th rowspan="4" valign="top">university</th>
      <th>original_condition</th>
      <th>electrical_equipment</th>
      <th>TEK07</th>
      <th>2019</th>
      <td>34.458</td>
      <td>195999.154</td>
      <td>6753804.164</td>
      <td>DH</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>0.990</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
      <td>6753804.164</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>6753804.164</td>
      <td>6753804.164</td>
      <td>6.754</td>
    </tr>
    <tr>
      <th>renovation</th>
      <th>electrical_equipment</th>
      <th>TEK07</th>
      <th>2019</th>
      <td>34.458</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>DH</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>0.990</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>renovation_and_small_measure</th>
      <th>electrical_equipment</th>
      <th>TEK07</th>
      <th>2019</th>
      <td>34.458</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>DH</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>0.990</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
    </tr>
    <tr>
      <th>small_measure</th>
      <th>electrical_equipment</th>
      <th>TEK07</th>
      <th>2019</th>
      <td>34.458</td>
      <td>5749.846</td>
      <td>198130.127</td>
      <td>DH</td>
      <td>1.000</td>
      <td>1.000</td>
      <td>0.990</td>
      <td>0.000</td>
      <td>1.000</td>
      <td>0.000</td>
      <td>1</td>
      <td>0.990</td>
      <td>1</td>
      <td>4</td>
      <td>198130.127</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>198130.127</td>
      <td>198130.127</td>
      <td>0.198</td>
    </tr>
  </tbody>
</table>
</div>




```python

# ['heating_rv']
d2.loc[(slice(None), slice(None), ['heating_dhw'], ['TEK07'], [2019])].groupby(by=['building_category', 'tek', 'purpose']).sum()

```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th>kwh_m2</th>
      <th>m2</th>
      <th>energy_requirement</th>
      <th>Oppvarmingstyper</th>
      <th>tek_share</th>
      <th>Grunnlast andel</th>
      <th>Grunnlast virkningsgrad</th>
      <th>Spisslast andel</th>
      <th>Spisslast virkningsgrad</th>
      <th>Ekstralast andel</th>
      <th>Ekstralast virkningsgrad</th>
      <th>Tappevann virkningsgrad</th>
      <th>Spesifikt elforbruk</th>
      <th>Kjoling virkningsgrad</th>
      <th>eq_ts</th>
      <th>RV_GL</th>
      <th>RV_SL</th>
      <th>RV_EL</th>
      <th>DHW_TV</th>
      <th>CL_KV</th>
      <th>O_SV</th>
      <th>sums</th>
      <th>gsums</th>
    </tr>
    <tr>
      <th>building_category</th>
      <th>tek</th>
      <th>purpose</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>apartment_block</th>
      <th>TEK07</th>
      <th>heating_dhw</th>
      <td>1547.982</td>
      <td>49673030.283</td>
      <td>1478710919.266</td>
      <td>ElectricityElectricit...</td>
      <td>4.000</td>
      <td>46.200</td>
      <td>99.640</td>
      <td>5.200</td>
      <td>47.200</td>
      <td>0.600</td>
      <td>52</td>
      <td>99.480</td>
      <td>52</td>
      <td>208</td>
      <td>113746993.790</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>71791658.889</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>71791658.889</td>
      <td>71.792</td>
    </tr>
    <tr>
      <th>culture</th>
      <th>TEK07</th>
      <th>heating_dhw</th>
      <td>80.180</td>
      <td>507434.000</td>
      <td>5085757.265</td>
      <td>ElectricityDHElectric...</td>
      <td>4.000</td>
      <td>8.000</td>
      <td>7.960</td>
      <td>0.000</td>
      <td>8.000</td>
      <td>0.000</td>
      <td>8</td>
      <td>7.880</td>
      <td>8</td>
      <td>32</td>
      <td>2542878.633</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>2571832.330</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>2571832.330</td>
      <td>2.572</td>
    </tr>
    <tr>
      <th>hospital</th>
      <th>TEK07</th>
      <th>heating_dhw</th>
      <td>119.078</td>
      <td>312368.000</td>
      <td>9299021.822</td>
      <td>DHDHDHDH</td>
      <td>4.000</td>
      <td>4.000</td>
      <td>3.960</td>
      <td>0.000</td>
      <td>4.000</td>
      <td>0.000</td>
      <td>4</td>
      <td>3.960</td>
      <td>4</td>
      <td>16</td>
      <td>9299021.822</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>9392951.336</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>9392951.336</td>
      <td>9.393</td>
    </tr>
    <tr>
      <th>hotel</th>
      <th>TEK07</th>
      <th>heating_dhw</th>
      <td>476.547</td>
      <td>2110264.000</td>
      <td>62852454.687</td>
      <td>ElectricityElectricit...</td>
      <td>4.000</td>
      <td>14.200</td>
      <td>23.960</td>
      <td>1.200</td>
      <td>14.520</td>
      <td>0.600</td>
      <td>16</td>
      <td>23.800</td>
      <td>16</td>
      <td>64</td>
      <td>15713113.672</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>13866769.986</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>13866769.986</td>
      <td>13.867</td>
    </tr>
    <tr>
      <th>house</th>
      <th>TEK07</th>
      <th>heating_dhw</th>
      <td>1667.750</td>
      <td>153491303.463</td>
      <td>4571162881.255</td>
      <td>ElectricityElectricit...</td>
      <td>4.000</td>
      <td>42.400</td>
      <td>103.640</td>
      <td>9.000</td>
      <td>49.960</td>
      <td>4.600</td>
      <td>56</td>
      <td>79.160</td>
      <td>56</td>
      <td>224</td>
      <td>326511634.375</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>328257221.068</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>328257221.068</td>
      <td>328.257</td>
    </tr>
    <tr>
      <th>kindergarten</th>
      <th>TEK07</th>
      <th>heating_dhw</th>
      <td>240.560</td>
      <td>1709910.000</td>
      <td>17138997.900</td>
      <td>ElectricityElectricit...</td>
      <td>4.000</td>
      <td>21.600</td>
      <td>39.880</td>
      <td>1.800</td>
      <td>22.440</td>
      <td>0.600</td>
      <td>24</td>
      <td>39.720</td>
      <td>24</td>
      <td>96</td>
      <td>2856499.650</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>2698263.632</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>2698263.632</td>
      <td>2.698</td>
    </tr>
    <tr>
      <th>nursing_home</th>
      <th>TEK07</th>
      <th>heating_dhw</th>
      <td>595.683</td>
      <td>3183795.000</td>
      <td>94826680.913</td>
      <td>ElectricityDHElectric...</td>
      <td>4.000</td>
      <td>19.400</td>
      <td>27.720</td>
      <td>0.600</td>
      <td>19.920</td>
      <td>0.000</td>
      <td>20</td>
      <td>27.640</td>
      <td>20</td>
      <td>80</td>
      <td>18965336.183</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>18283863.359</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>18283863.359</td>
      <td>18.284</td>
    </tr>
    <tr>
      <th>office</th>
      <th>TEK07</th>
      <th>heating_dhw</th>
      <td>200.444</td>
      <td>18413610.000</td>
      <td>92272645.667</td>
      <td>ElectricityElectricit...</td>
      <td>4.000</td>
      <td>35.800</td>
      <td>79.720</td>
      <td>3.600</td>
      <td>38.240</td>
      <td>0.600</td>
      <td>40</td>
      <td>79.560</td>
      <td>40</td>
      <td>160</td>
      <td>9227264.567</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>6225585.912</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>6225585.912</td>
      <td>6.226</td>
    </tr>
    <tr>
      <th>retail</th>
      <th>TEK07</th>
      <th>heating_dhw</th>
      <td>377.400</td>
      <td>25017948.000</td>
      <td>262271488.200</td>
      <td>ElectricityDHElectric...</td>
      <td>4.000</td>
      <td>33.000</td>
      <td>75.720</td>
      <td>3.000</td>
      <td>35.640</td>
      <td>0.000</td>
      <td>36</td>
      <td>75.640</td>
      <td>36</td>
      <td>144</td>
      <td>29141276.467</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>17658283.548</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>17658283.548</td>
      <td>17.658</td>
    </tr>
    <tr>
      <th>school</th>
      <th>TEK07</th>
      <th>heating_dhw</th>
      <td>196.083</td>
      <td>6097075.000</td>
      <td>59776739.479</td>
      <td>ElectricityElectricit...</td>
      <td>4.000</td>
      <td>18.200</td>
      <td>27.800</td>
      <td>1.200</td>
      <td>18.520</td>
      <td>0.600</td>
      <td>20</td>
      <td>27.640</td>
      <td>20</td>
      <td>80</td>
      <td>11955347.896</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>12038370.266</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>12038370.266</td>
      <td>12.038</td>
    </tr>
    <tr>
      <th>sports</th>
      <th>TEK07</th>
      <th>heating_dhw</th>
      <td>1372.560</td>
      <td>4060273.000</td>
      <td>199034582.460</td>
      <td>ElectricityElectricit...</td>
      <td>4.000</td>
      <td>25.600</td>
      <td>43.720</td>
      <td>1.800</td>
      <td>26.440</td>
      <td>0.600</td>
      <td>28</td>
      <td>43.560</td>
      <td>28</td>
      <td>112</td>
      <td>28433511.780</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>23932378.171</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>23932378.171</td>
      <td>23.932</td>
    </tr>
    <tr>
      <th>storage_repairs</th>
      <th>TEK07</th>
      <th>heating_dhw</th>
      <td>400.900</td>
      <td>5170520.000</td>
      <td>51821536.700</td>
      <td>ElectricityElectricit...</td>
      <td>4.000</td>
      <td>36.200</td>
      <td>71.680</td>
      <td>3.200</td>
      <td>36.880</td>
      <td>0.600</td>
      <td>40</td>
      <td>71.520</td>
      <td>40</td>
      <td>160</td>
      <td>5182153.670</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>3706226.554</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>3706226.554</td>
      <td>3.706</td>
    </tr>
    <tr>
      <th>university</th>
      <th>TEK07</th>
      <th>heating_dhw</th>
      <td>20.044</td>
      <td>201749.000</td>
      <td>1010986.656</td>
      <td>DHDHDHDH</td>
      <td>4.000</td>
      <td>4.000</td>
      <td>3.960</td>
      <td>0.000</td>
      <td>4.000</td>
      <td>0.000</td>
      <td>4</td>
      <td>3.960</td>
      <td>4</td>
      <td>16</td>
      <td>1010986.656</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>1021198.642</td>
      <td>0.000</td>
      <td>0.000</td>
      <td>1021198.642</td>
      <td>1.021</td>
    </tr>
  </tbody>
</table>
</div>



### Write d2 to disk


```python
filename = 'output/ebm-tek-andeler-merge-teks.xlsx'
d2.to_excel(filename, merge_cells=False, freeze_panes=(1, 5))
print(f'Wrote {filename}')
```

    Wrote output/ebm-tek-andeler-merge-teks.xlsx
    


```python
filename = 'output/ebm-tek-andeler.csv'
d2.to_csv(filename)
print(f'Wrote {filename}')
```

    Wrote output/ebm-tek-andeler.csv
    
