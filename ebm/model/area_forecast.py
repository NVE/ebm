import typing
import pandas as pd

from loguru import logger

from ebm.model.data_classes import TEKParameters,YearRange
from ebm.model.building_condition import BuildingCondition
from ebm.model.building_category import BuildingCategory

# Possible issue in the future:
# - problemer med riving og nybygging kobling dersom tidshorisonten overstiger tidligste alder for riving på nye TEKer

class AreaForecast():
    """
    """

    def __init__(self,
                 building_category: BuildingCategory,
                 area_start_year: pd.Series,
                 tek_list: typing.List[str],   
                 tek_params: typing.Dict[str, TEKParameters], 
                 shares_per_condtion: typing.Dict[BuildingCondition, typing.Dict[str, pd.Series]],
                 period: YearRange = YearRange(2010, 2050)) -> None:

        self.building_category = building_category
        self.area_start_year = area_start_year
        self.tek_list = tek_list
        self.tek_params = tek_params                                  
        self.shares_per_condition = shares_per_condtion  
        self.period = period

    def __repr__(self):
        return f'AreaForecast(building_category="{self.building_category}", period={self.period})'

    def calc_area_pre_construction(self, tek: str, building_condition: BuildingCondition) -> pd.Series:
        """
        Calculates the floor area over the model period for a given building condition and TEK used prior to construction.

        Construction of new buildings first begins in the model start year. Thus, this method only works for TEKs that are
        used before the model period begins. For these TEK's, the floor area is calculated by multiplying the floor area of
        the TEK in the model start year with the building condition share for each year in the model period.
        
        Parameters
        ----------
        tek : str
            The TEK identifier to calculate the area for.
        building_condition : BuildingCondition
            The building condition for which the area is being calculated.

        Returns
        -------
        pandas.Series
            A `pandas.Series` representing the floor area per year for the given building condition and TEK.

        Raises
        ------
        ValueError
            If the given TEK isn't used before the model period begins.
        """
        tek_start_year = self.tek_params[tek].start_year
        tek_end_year = self.tek_params[tek].end_year
        if tek_end_year >= self.period.start:
            msg = (f"Invalid tek parameter: {tek}. Method only works for TEK's that are used before the model period begins. " 
                   f"{tek} is used from {tek_start_year} to {tek_end_year}, while the model period begins in {self.period.start}.")
            raise ValueError(msg)

        area_start_year = self.area_start_year[tek]
        
        shares = self.shares_per_condition[building_condition][tek]
        area = shares * area_start_year
        area.rename("area", inplace=True)
        
        return area
    
    def calc_area_pre_construction_per_tek_condition(self) -> typing.Dict[str, typing.Dict[BuildingCondition, pd.Series]]:
        """
        Calculates the floor area per building condition over the model period for all TEK's used prior to construction.

        For each TEK, the floor area is calculated for each building condition, provided that the TEK is used before the
        model start year. The calculation is performed by multiplying the floor area in the model start year with the 
        building condition share for each year in the model period.

        Returns
        -------
        dict of str to dict of BuildingCondition to pandas.Series
            A nested dictionary where:
            - Keys are TEK identifiers as strings.
            - Values are dictionaries where:
                - Keys are `BuildingCondition` objects.
                - Values are `pandas.Series` representing the floor area for each building condition over the model period.
        """
        area_per_tek = {}
        for tek in self.tek_list:
            tek_end_year = self.tek_params[tek].end_year
            # Control that the TEK period is before the model start year (when new buildings are constructed)
            if tek_end_year < self.period.start:

                area_per_condition = {}
                for building_condition in BuildingCondition:
                    area = self.calc_area_pre_construction(tek, building_condition)
                    area_per_condition[building_condition] = area

                area_per_tek[tek] = area_per_condition

        return area_per_tek 
                
    def calc_total_demolition_area_per_year(self) -> pd.Series:
        """
        Aggregates the floor area that's demolished per model year across all TEK's used prior to construction. 

        Returns
        -------
        pandas.Series
            A `pandas.Series` representing the total demolished floor area for each year in the model period.
        """
        area_pre_construction = self.calc_area_pre_construction_per_tek_condition()
        
        acc_total_demolition = pd.Series(0.0, index=self.period)
        for tek in area_pre_construction:
            acc_total_demolition += area_pre_construction[tek][BuildingCondition.DEMOLITION]

        acc_total_demolition.index.name = 'year'
        acc_total_demolition.rename(BuildingCondition.DEMOLITION, inplace=True)

        total_demolition_per_year = acc_total_demolition.diff().fillna(0)

        return total_demolition_per_year
    
    def calc_area_with_construction(self,
                                    tek: str,
                                    building_condition: BuildingCondition,
                                    accumulated_constructed_floor_area: pd.Series) -> pd.Series:
        """
        Calculates the floor area over the model period for a given building condition and TEK used in a period with
        construction.

        The calculations are performed as follows:
        - For years within the TEK's period, the area is determined by multiplying the building condition shares with
            the sum of the TEK's start year area and the accumulated constructed floor area, adjusted for the
            constructed area that existed before the TEK's period began.
        - For years after the TEK's period, the area is determined by multiplying the building condition shares with
            the TEK's start year area plus the accumulated constructed floor area at the end of the TEK's period.

        Parameters
        ----------
        tek : str
            The TEK identifier to calculate the area for.
        building_condition : BuildingCondition
            The building condition for which the area is being calculated.
        accumulated_constructed_floor_area : pandas.Series
            A series representing the accumulated constructed floor area up to each year in the model period.

        Returns
        -------
        pandas.Series
            A `pandas.Series` representing the floor area for each year during the model period.

        Raises
        ------
        ValueError
            If the given TEK isn't used in a period with construction, which is from the start of the model period.
        """
        tek_start_year = self.tek_params[tek].start_year
        tek_end_year = self.tek_params[tek].end_year
        if tek_end_year < self.period.start:
            logger.error("Method only works for TEK's that are used after or during the start of model period.")
            logger.error("f{tek=} {tek_start_year=} {tek_end_year=} {self.period.start=}")
            msg = f"Invalid tek {tek}. tek start year is before model end year"
            raise ValueError(msg)

        area = pd.Series(0.0, index=self.period.to_index(), name='area')
        shares = self.shares_per_condition[building_condition][tek]
        
        try:
            # Retrieve area in start year
            area_start_year = self.area_start_year[tek]
        except KeyError:
            # Set to 0 if TEK isn't present in area series
            area_start_year = 0.0        
        
        try:
            # Retrieve accumulated construction area from before the TEK period begins
            acc_construction_pre_tek_period = accumulated_constructed_floor_area.loc[tek_start_year - 1] 
        except KeyError:
            # Set to 0 if the year before the TEK period begins isn't present in index, i.e. if the tek period starts
            #  before the model period
            acc_construction_pre_tek_period = 0.0

        end_year_filter = min(tek_end_year, max(accumulated_constructed_floor_area.index.values))
        acc_construction_end_tek_period = accumulated_constructed_floor_area.loc[end_year_filter]

        # Create year masks for different calculation methods across the model period
        tek_period_mask = (tek_start_year <= area.index) & (area.index <= tek_end_year)
        post_tek_period_mask = area.index > tek_end_year

        # Increase the accumulated construction area in the TEK period
        area[tek_period_mask] = shares[tek_period_mask] * (area_start_year + accumulated_constructed_floor_area[
            tek_period_mask] - acc_construction_pre_tek_period)

        # Hold the accumulated construction area constant after the TEK period 
        area[post_tek_period_mask] = shares[post_tek_period_mask] * (area_start_year + acc_construction_end_tek_period -
                                                                     acc_construction_pre_tek_period)

        return area
    
    def calc_area_with_construction_per_tek_condition(self, accumulated_constructed_floor_area: pd.Series) -> typing.Dict[str, typing.Dict[BuildingCondition, pd.Series]]:
        """
        Calculates the floor area per building condition over the model period for all TEK's used in a period with construction.

        The calculations are performed as follows:
        - For years within the TEK's period, the area is determined by multiplying the building condition shares with the sum 
          of the TEK's start year area and the accumulated constructed floor area, adjusted for the constructed area that existed
          before the TEK's period began.
        - For years after the TEK's period, the area is determined by multiplying the building condition shares with the TEK's 
          start year area plus the accumulated constructed floor area at the end of the TEK's period.

        Parameters
        ----------
        accumulated_constructed_floor_area : pandas.Series
            A series representing the accumulated constructed floor area up to each year in the model period.

        Returns
        -------
        dict of str to dict of BuildingCondition to pandas.Series
            A nested dictionary where:
            - Keys are TEK identifiers as strings.
            - Values are dictionaries where:
                - Keys are `BuildingCondition` objects.
                - Values are `pandas.Series` representing the floor area for each building condition over the model period.
        """
        area_per_tek = {}
        for tek in self.tek_list:
            tek_end_year = self.tek_params[tek].end_year
            if self.period.start <= tek_end_year:

                area_per_condition = {}
                for building_condition in BuildingCondition:
                    area = self.calc_area_with_construction(tek, building_condition, accumulated_constructed_floor_area)
                    area_per_condition[building_condition] = area 
                
                area_per_tek[tek] = area_per_condition

        return area_per_tek

    def calc_area_dict(self, accumulated_constructed_floor_area: pd.Series) -> typing.Dict[str, typing.Dict[BuildingCondition, pd.Series]]:
        """
        Calculates the floor area per building condition over the model period for all TEK's in 'self.tek_list'.

        Parameters
        ----------
        accumulated_constructed_floor_area : pandas.Series
            A series representing the accumulated constructed floor area up to each year in the model period.

        Returns
        -------
        dict of str to dict of BuildingCondition to pandas.Series
            A nested dictionary where:
            - Keys are TEK identifiers as strings.
            - Values are dictionaries where:
                - Keys are `BuildingCondition` objects.
                - Values are `pandas.Series` representing the floor area for each building condition over the model period.
        """
        area_pre_construction = self.calc_area_pre_construction_per_tek_condition()
        area_with_construction = self.calc_area_with_construction_per_tek_condition(accumulated_constructed_floor_area)

        # Combine dictionaries 
        area = area_pre_construction.copy()
        for tek in area_with_construction:
            area[tek] = area_with_construction[tek]
        
        return area


    def calc_area(self, accumulated_constructed_floor_area: pd.Series) -> pd.DataFrame:
        """
        Calculates the floor area per building condition over the model period for all TEK's in 'self.tek_list'.

        Parameters
        ----------
        accumulated_constructed_floor_area : pandas.Series
           A series representing the accumulated constructed floor area up to each year in the model period.

        Returns
        -------
        pd.DataFrame
        """
        # Temporary method to convert series to list
        forecast = self.calc_area_dict(accumulated_constructed_floor_area)

        def forecast_to_dataframe():
            def flatten_forecast():
                for tek, conditions in forecast.items():
                    for condition, floor_area in conditions.items():
                        for year, value in floor_area.items():
                            yield tek, condition, year, value,

            flat = pd.DataFrame(flatten_forecast(),
                                columns=['TEK', 'building_condition', 'year', 'm2'])
            return flat

        df = forecast_to_dataframe()
        return df

