import ebm
import pathlib

def test_dataset_readme_md_use_uppercase():
    """Ensure that each dataset in ebm/data has a README.md file and that the filename uses the correct case.

The filename must use an uppercase stem ('README') and a lowercase extension ('.md').
    """
    data_path = pathlib.Path(ebm.__file__).parent / 'data'
    assert data_path.is_dir(), 'No ebm/data directory found'

    for population_forecast_csv in data_path.glob('*/population_forecast.csv'):
        dataset = population_forecast_csv.parent

        readmes = [f for f in dataset.iterdir() if f.name.lower() == 'readme.md']
        assert len(readmes) == 1, f'Expected exactly 1 README.md in {dataset}. Got {len(readmes)} {readmes}'

        readme = readmes[0]
        assert readme.is_file(), f'dataset {dataset.name} is missing README.md'
        assert readme.name == 'README.md', f'README.md in dataset `{dataset.name}`  has the wrong case. Expected: README.md GOT: {readme.name}'

