import pandas as pd

from ebm.model import DatabaseManager


class NewBuildings:
    def create_new_building_dataframe(self, population: pd.Series,
                                      household_size: pd.Series,
                                      building_category_share: pd.DataFrame,
                                      build_area_sum: pd.DataFrame,
                                      yearly_demolished_floor_area: pd.Series,
                                      average_floor_area=175) -> pd.DataFrame:
        # Befolkningsøkning (Ikke brukt videre)
        population_growth = self.calculate_population_growth(population)
        households = self.calculate_households_by_year(household_size, population)

        # Årlig endring i antall boliger (brukt Årlig endring i antall småhus)
        households_change = self.calculate_household_change(households)
        house_change = self.calculate_house_change(building_category_share, households_change, average_floor_area)

        # Årlig endring areal småhus (brukt Årlig nybygget areal småhus)
        yearly_floor_area_change = self.calculate_yearly_floor_area_change(
            building_category_share['new_house_share'] if average_floor_area == 175 else building_category_share[
                'new_apartment_block_share'],
            house_change, average_floor_area)

        # Årlig revet areal småhus
        yearly_demolition_floor_area = self.calculate_yearly_new_building_floor_area(
            build_area_sum, yearly_floor_area_change, yearly_demolished_floor_area)

        # Nybygget småhus akkumulert
        floor_area_change_accumulated = self.calculate_yearly_new_building_floor_area_sum(yearly_demolition_floor_area)

        df = pd.DataFrame(data=[
            population,
            population_growth,
            household_size,
            households,
            households_change,
            house_change,
            yearly_floor_area_change,
            yearly_demolished_floor_area,
            yearly_demolition_floor_area,
            floor_area_change_accumulated])

        return df

    @staticmethod
    def calculate_yearly_new_building_floor_area_sum(yearly_new_building_floor_area_house: pd.Series):
        return pd.Series(yearly_new_building_floor_area_house.cumsum(), name='floor_area_change_accumulated')

    @staticmethod
    def calculate_yearly_new_building_floor_area(build_area_sum,
                                                 yearly_floor_area_change,
                                                 yearly_demolished_floor_area) -> pd.Series:
        # Årlig nybygget areal småhus (brukt  Nybygget småhus akkumulert)
        yearly_new_building_floor_area_house = yearly_floor_area_change + yearly_demolished_floor_area
        yearly_new_building_floor_area_house.loc[build_area_sum.index.values] = build_area_sum.loc[
            build_area_sum.index.values]

        return pd.Series(yearly_new_building_floor_area_house, name='new_building_floor_area')

    @staticmethod
    def calculate_floor_area_demolished(row=655):
        # Loading demolition data from spreadsheet. Should be changed to a parameter with calculated data
        demolition = DatabaseManager().load_demolition_floor_area_from_spreadsheet(
            'house' if row == 656 else 'apartment_block')
        # Årlig revet areal småhus
        yearly_demolished_floor_area_house = demolition.diff(1)
        return pd.Series(yearly_demolished_floor_area_house, name='demolition_change')

    @staticmethod
    def calculate_yearly_floor_area_change(building_category_share: pd.Series, house_change: pd.Series,
                                           average_floor_area=175) -> pd.Series:
        yearly_floor_area_change = average_floor_area * house_change
        yearly_floor_area_change.loc[[2010, 2011]] = 0
        return pd.Series(yearly_floor_area_change, name='house_floor_area_change')

    @staticmethod
    def calculate_population_growth(population):
        population_growth = (population / population.shift(1)) - 1
        return pd.Series(population_growth, name='population_growth')

    @staticmethod
    def calculate_house_change(building_category_share: pd.DataFrame, households_change: pd.Series,
                               average_floor_area=175) -> pd.Series:
        house_share = building_category_share['new_house_share'] if average_floor_area == 175 else \
            building_category_share['new_apartment_block_share']
        # Årlig endring i antall småhus (brukt  Årlig endring areal småhus)
        house_change = households_change * house_share
        return pd.Series(house_change, name='house_change')

    @staticmethod
    def calculate_household_change(households: pd.Series) -> pd.Series:
        return pd.Series(households - households.shift(1), name='household_change')

    @staticmethod
    def calculate_households_by_year(household_size: pd.Series, population: pd.Series) -> pd.Series:
        # Husholdninger
        households = population / household_size
        return pd.Series(households, name='households')
