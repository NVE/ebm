from ebm.model import BuildingCategory
from ebm.model.bema import beregne_energibehov
from ebm.services.console import rich_display_dataframe


def main():
    building_category = BuildingCategory.KINDERGARTEN
    df = beregne_energibehov(building_category)

    print('=== ', building_category, ' === ')
    rich_display_dataframe(df)

    return df


df = None

if __name__ == '__main__':
    df = main()
