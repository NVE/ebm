import typing

from ebm.model.data_classes import TEKParameters
from ebm.model.tek import TEK
from ebm.model.building_condition import BuildingCondition

class SharesPerCondition():
    """
    Calculates area shares over time per condition for all TEKs within a building category.
    """
    
    # TODO: 
    # - add start and end year as input arguments, as they should be defined outside the class
    # - add negative values checks 
    # - add checks to control calculations, for example control total values and that original condition should not exceed 100%
    # - make code less repetative (e.g for loops on tek_list -> change to own method?)

    def __init__(self, 
                 tek_list: typing.List[str], 
                 tek_params: typing.Dict[str, TEKParameters], 
                 scurve_data: typing.Dict[str, typing.List[typing.Tuple[typing.Tuple[float], float]]],
                 model_start_year: int = 2010,
                 model_end_year: int = 2050):
        
        self.tek_list = tek_list
        self.tek = TEK(tek_params)
        self.scurve_data = scurve_data
        self.model_start_year = model_start_year
        self.model_end_year = model_end_year

        # Define S-curve parameter attributes 
        self.scurve_small_measure = self.scurve_data[BuildingCondition.SMALL_MEASURE][0]
        self.scurve_renovation = self.scurve_data[BuildingCondition.RENOVATION][0]
        self.scurve_demolition = self.scurve_data[BuildingCondition.DEMOLITION][0]
        self.never_share_small_measure = self.scurve_data[BuildingCondition.SMALL_MEASURE][1]
        self.never_share_renovation = self.scurve_data[BuildingCondition.RENOVATION][1]
        self.never_share_demolition = self.scurve_data[BuildingCondition.DEMOLITION][1]
        
        self.shares_demolition = self.calc_shares_demolition()
        self.shares_small_measure_total = self.calc_shares_small_measure_total()
        self.shares_renovation_total = self.calc_shares_renovation_total()
        self.shares_renovation = self.calc_shares_renovation()
        self.shares_renovation_and_small_measure = self.calc_shares_renovation_and_small_measure()
        self.shares_small_measure = self.calc_shares_small_measure()
        self.shares_original_condition = self.calc_shares_original_condition()

        self.shares_per_condition = {
            BuildingCondition.SMALL_MEASURE: self.shares_small_measure,
            BuildingCondition.RENOVATION: self.shares_renovation,
            BuildingCondition.RENOVATION_AND_SMALL_MEASURE: self.shares_renovation_and_small_measure,
            BuildingCondition.DEMOLITION: self.shares_demolition,
            BuildingCondition.ORIGINAL_CONDITION: self.shares_original_condition
        }
        
    def calc_shares_demolition(self) -> typing.Dict:
        """
        Calculate the percentage share of area that is demolished over time for each TEK.

        This method calculates the percentage share of demolition for each year 
        from the start year to the end year for all TEKs in `self.tek_list`. 
        It uses the accumulated rates from the demolition S-curve to determine the 
        share of demolition. The share is calculated by subtracting the rate for 
        the current year from the rate for the previous year.

        For each TEK:
        - The share is set to 0 in the start year, and if the building hasn't been
        built yet (building year of the TEK is after the current year).
        - The share is set to the rate of the current year in the building year of the 
        TEK if that year is after the start year.  

        Returns:
        - tek_shares (dict): A dictionary where each key is a TEK and the value is a 
                            list of demolition shares (float) for each year from the 
                            start year to the end year.
        """
        tek_shares = {}
        for tek in self.tek_list: 

            building_year = self.tek.get_building_year(tek)
            shares = []

            # Iterate over years from start to end year
            for year in range(self.model_start_year, self.model_end_year + 1):
                building_age = year - building_year
                
                if year == self.model_start_year or building_year >= year:
                    # Set share to 0 in the start year and if the building isn't buildt yet
                    share = 0
                elif building_year == year - 1:
                    # Set share to the current rate/share if the building year is equal to year-1
                    rate = self.scurve_demolition[building_age - 1]
                else:
                    # Get rates/shares from the demolition S-curve based on building age
                    rate = self.scurve_demolition[building_age - 1]
                    prev_rate = self.scurve_demolition[building_age - 2]

                    # Calculate percentage share by subtracting rate from previous year's rate
                    share = rate - prev_rate   
                
                shares.append(share)

            # Accumulate shares over the time horizon
            accumulated_shares = []
            acc_share = 0
            for share in shares:
                acc_share += share
                accumulated_shares.append(acc_share)

            tek_shares[tek] = accumulated_shares

        return tek_shares
    
    def calc_shares_small_measure_total(self) -> typing.Dict:
        """
        Calculate the percentage share of area that have undergone small measures over the time horizon for each TEK.

        This method calculates the percentage share of area that have undergone small measures 
        for each year from the start year to the end year. This share doesn't refer to area that 
        only have undergone a small measure, as the area may also have undergone renovation. 
        It uses the accumulated rates from the small measures S-curve.

        Returns:
        - tek_shares (dict): A dictionary where the keys are TEK's and the values are lists of 
                            small measures renovation shares (float) for each year from the start 
                            year to the end year.
        """
        tek_shares = {}
        
        for tek in self.tek_list: 

            building_year = self.tek.get_building_year(tek)
            shares =  []

            for idx, year in enumerate(range(self.model_start_year, self.model_end_year + 1)):
                
                building_age = year - building_year

                if building_year >= year:
                    # Set share to 0 if the building isn't buildt yet
                    share = 0
                else:
                    # Get Small measure share from S-curve and demolition share for current year
                    small_measure_share = self.scurve_small_measure[building_age - 1]
                    demolition_share = self.shares_demolition[tek][idx] 
                    
                    # Calculate max limit for doing a renovation measure (small measure or rehabilitation)
                    measure_limit = 1 - demolition_share - self.never_share_small_measure
                    
                    if small_measure_share < measure_limit:
                        share = small_measure_share
                    else: 
                        share = measure_limit
                
                shares.append(share)
            tek_shares[tek] = shares
        return tek_shares
    
    def calc_shares_renovation_total(self) -> typing.Dict:
        """
        Calculate the percentage share of area that is renovated over time for each TEK.

        This method calculates the percentage share of renovations for each year 
        from the start year to the end year. It uses the accumulated rates from the 
        renovation S-curve.

        Returns:
        - tek_shares (dict): A dictionary where the keys are TEK's and the values are lists of 
                            renovation shares (float) for each year from the start year to the 
                            end year.
        """
        tek_shares = {}
        
        for tek in self.tek_list: 

            building_year = self.tek.get_building_year(tek)
            shares =  []

            for idx, year in enumerate(range(self.model_start_year, self.model_end_year + 1)):
                building_age = year - building_year

                if building_year >= year:
                    # Set share to 0 if the building isn't buildt yet
                    share = 0
                else:
                    # Get renovation share from S-curve and demolition share for current year
                    renovation_share = self.scurve_renovation[building_age - 1]
                    demolition_share = self.shares_demolition[tek][idx]                
                    
                    # Calculate max limit for doing a renovation measure (small measure or renovation)
                    measure_limit = 1 - demolition_share - self.never_share_renovation
                    
                    if renovation_share < measure_limit:
                        share = renovation_share
                    else: 
                        share = measure_limit 
                
                shares.append(share)
            tek_shares[tek] = shares    
        return tek_shares

    def calc_shares_renovation(self) -> typing.Dict:
        """
        Calculate the percentage share of area that is renovated (only renovation) over time for each TEK.

        This method calculates the percentage share of renovation for each year 
        from the start year to the end year for all TEKs in `self.tek_list`. 
        It considers buildings that have only undergone renovation and not any other measures. 
        The calculation takes into account the total shares of small measures, 
        renovation, and demolition to determine the valid renovation share.

        Returns:
        - tek_shares (dict): A dictionary where each key is a TEK and the value is a 
                            list of renovation shares (float) for each year from the 
                            start year to the end year.
        """
        tek_shares = {}
        
        for tek in self.tek_list: 

            building_year = self.tek.get_building_year(tek)
            shares =  []

            for idx, year in enumerate(range(self.model_start_year, self.model_end_year + 1)):

                if building_year >= year:
                    # Set share to 0 if the building isn't buildt yet
                    share = 0
                else:
                    share_small_measure_total = self.shares_small_measure_total[tek][idx]
                    share_renovation_total = self.shares_renovation_total[tek][idx]
                    share_demolition = self.shares_demolition[tek][idx]  
                    measure_limit = 1- share_demolition - self.never_share_renovation 

                    if (share_small_measure_total + share_renovation_total) < measure_limit:
                        share = share_renovation_total
                    elif share_small_measure_total > measure_limit:
                        share = 0
                    else:
                        share = measure_limit - share_small_measure_total

                shares.append(share)
            tek_shares[tek] = shares
        return tek_shares

    def calc_shares_renovation_and_small_measure(self) -> typing.Dict:
        """
        Calculate the percentage share of area that has undergone both renovation and small measures over time for each TEK.

        This method calculates the percentage share of areas that have undergone both renovation 
        and small measures for each year from the start year to the end year for all TEKs in `self.tek_list`. 
        The share is calculated by subtracting the renovation share from the total renovation share.

        Returns:
        - tek_shares (dict): A dictionary where each key is a TEK and the value is a 
                            list of renovation and small measures shares (float) for each year from the 
                            start year to the end year.
        """
        tek_shares = {}
        
        for tek in self.tek_list: 

            building_year = self.tek.get_building_year(tek)
            shares =  []

            for idx, year in enumerate(range(self.model_start_year, self.model_end_year + 1)):

                if building_year >= year:
                    # Set share to 0 if the building isn't buildt yet
                    share = 0
                else:
                    share_renovation_total = self.shares_renovation_total[tek][idx]
                    share_renovation = self.shares_renovation[tek][idx]
                    share = share_renovation_total - share_renovation
                
                shares.append(share)
            tek_shares[tek] = shares
        return tek_shares
    
    def calc_shares_small_measure(self) -> typing.Dict:
        """
        Calculate the percentage share of area that has undergone only small measures over time for each TEK.

        This method calculates the percentage share of small measures for each year 
        from the start year to the end year for all TEKs in `self.tek_list`. 
        The share is calculated by subtracting the combined share of renovation 
        and small measures from the total small measures share.

        Returns:
        - tek_shares (dict): A dictionary where each key is a TEK and the value is a 
                            list of small measures shares (float) for each year from the 
                            start year to the end year.
        """
        tek_shares = {}
        
        for tek in self.tek_list: 

            building_year = self.tek.get_building_year(tek)
            shares =  []

            for idx, year in enumerate(range(self.model_start_year, self.model_end_year + 1)):

                if building_year >= year:
                    # Set share to 0 if the building isn't buildt yet
                    share = 0
                else:
                    share_small_measure_total = self.shares_small_measure_total[tek][idx]
                    share_renovation_and_small_measure = self.shares_renovation_and_small_measure[tek][idx]
                    share = share_small_measure_total - share_renovation_and_small_measure
                
                shares.append(share)
            tek_shares[tek] = shares
        return tek_shares
    
    def calc_shares_original_condition(self) -> typing.Dict:
        """
        Calculate the percentage share of area that remains in its original condition over time for each TEK.

        This method calculates the percentage share of areas that remain in their original condition 
        for each year from the start year to the end year for all TEKs in `self.tek_list`. 
        The share is calculated by subtracting the shares of small measures, renovation, 
        combined renovation and small measures, and demolition from 1.

        Returns:
        - tek_shares (dict): A dictionary where each key is a TEK and the value is a 
                            list of shares of original condition (float) for each year from the 
                            start year to the end year.
        """
        tek_shares = {}
        
        for tek in self.tek_list: 

            tek_start_year = self.tek.get_start_year(tek)
            shares =  []

            for idx, year in enumerate(range(self.model_start_year, self.model_end_year + 1)):
                # Set share to 0 in years before the start year of the TEK if the TEK start year is after the start year of the model horizon
                if (tek_start_year > self.model_start_year) and (year < tek_start_year ):
                    share = 0
                else:
                    share_small_measure = self.shares_small_measure[tek][idx]
                    share_renovation = self.shares_renovation[tek][idx]
                    share_renovation_and_small_measure = self.shares_renovation_and_small_measure[tek][idx]
                    share_demolition = self.shares_demolition[tek][idx]
                    share = 1 - share_small_measure - share_renovation - share_renovation_and_small_measure - share_demolition  

                shares.append(share)
            tek_shares[tek] = shares
        return tek_shares     
        


if __name__ == '__main__':
    
    from ebm.model.buildings import Buildings
    from ebm.model.building_category import BuildingCategory
    from ebm.model.database_manager import DatabaseManager

    database_manager = DatabaseManager()
    building_category = BuildingCategory.HOUSE
    condition = BuildingCondition

    building = Buildings.build_buildings(building_category, database_manager)
    shares = building.get_shares()
    shares = building.get_shares_per_condition('small_measure')
   
    print(shares)






