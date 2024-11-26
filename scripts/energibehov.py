from ebm.model import BuildingCategory
from ebm.model.bema import beregne_energibehov
from ebm.services.console import rich_display_dataframe


def main():
    building_category = BuildingCategory.KINDERGARTEN
    df = beregne_energibehov(building_category)
    df.loc[:, 'sum'] = df.heating_rv + df.fans_and_pumps + df.heating_dhw + df.lighting + df.electrical_equipment + df.cooling

    print('=== ', building_category, ' === ')
    rich_display_dataframe(df)

    return df


df = None

if __name__ == '__main__':
    df = main()
