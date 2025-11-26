
"""
Generate S-curves from calibrated CSV parameters.

This module reads S-curve parameters from a CSV file, optionally filters them using a pandas query,
and computes S-curves for each parameter set using the `SCurve` model. The results are returned as
a combined pandas DataFrame and can optionally be saved to a CSV file.

Notes
-----
- Requires Python 3.10 or later.
- Uses `loguru` for logging and `pandas` for data manipulation.
- The S-curve calculation logic is implemented in `ebm.model.scurve.SCurve`.

Examples
--------
Run the script from the command line:

.. code-block:: bash

    python -m ebm.cmd.load_scurve data/calibrated/s_curve.csv --query "building_category == 'house'" --output results.csv


Optionally use python flag ``-i`` to work with the result in the python repl:

.. code-block:: bash

    python -i ebm/cmd/load_scurve.py data/calibrated/s_curve.csv --query "building_category == 'house'" --output results.csv


Functions
---------
generate_scurve_dataframe(s_curve_parameters)
    Generate a combined DataFrame of S-curves based on input parameters.

parse_arguments()
    Parse command-line arguments for CSV path, query, and output file.

main()
    Main entry point for generating S-curves.

Command-Line Arguments
----------------------
scurve_csv : str, optional
    Path to the S-curve CSV file. Defaults to ``data/calibrated/s_curve.csv``.
--query : str, optional
    Pandas query string to filter the input DataFrame.
--output : str, optional
    Path to save the generated S-curves as a CSV file.

Returns
-------
tuple of (pd.DataFrame | None, pd.DataFrame)
    A tuple containing the generated S-curves DataFrame (or None if no curves were generated)
    and the original or filtered parameter DataFrame.
"""

import argparse
import os
import pathlib
import sys

import pandas as pd
from loguru import logger
from pandas.errors import UndefinedVariableError

from ebm.cmd.helpers import configure_loglevel, load_environment_from_dotenv
from ebm.model.scurve import SCurve


def generate_scurve_dataframe(s_curve_parameters: pd.DataFrame) -> pd.DataFrame:
    """Generate a combined DataFrame of S-curves based on input parameters."""
    calc_scurve_results = []

    for params in s_curve_parameters.itertuples(index=False):
        logger.debug(params)

        try:
            scurve = SCurve(
                earliest_age=params.earliest_age_for_measure,
                average_age=params.average_age_for_measure,
                last_age=params.last_age_for_measure,
                rush_years=params.rush_period_years,
                never_share=params.never_share,
                rush_share=params.rush_share,
            )
            s_curve_series = scurve.get_rates_per_year_over_building_lifetime()
        except ValueError:
            logger.error(
                "Got ValueError while loading s-curve for {building_category} {building_condition}",
                building_category=getattr(params, "building_category", "unknown"),
                building_condition=getattr(params, "condition", "unknown"),
            )
            continue

        s_curve_df = s_curve_series.to_frame(name="share")
        s_curve_df['share_acc'] = s_curve_series.cumsum()

        s_curve_df = s_curve_df.assign(**params._asdict())
        s_curve_df = s_curve_df.rename(columns={'condition': 'building_condition'}, errors='ignore')
        calc_scurve_results.append(s_curve_df)

    df = pd.concat(calc_scurve_results) if calc_scurve_results else pd.DataFrame()
    df = df.reset_index()
    indexed=df.set_index(["building_category", "building_condition", "age"]) if 'age' in df.columns else df
    return indexed


def filter_s_curve_parameters(filter_query: str | None, scurve_parameters: pd.DataFrame) ->pd.DataFrame:
    """Filter S-curve parameters using a pandas query string."""
    if not filter_query:
        return scurve_parameters
    try:
        scurve_parameters = scurve_parameters.query(filter_query)
    except (KeyError, UndefinedVariableError):
        logger.error(
            'Invalid query? Got KeyError while using query "{query}" on dataframe.', query=filter_query,
        )
        sys.exit(1)
    return scurve_parameters


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    default_csv_path = pathlib.Path(__file__).parent.parent / "data/calibrated/s_curve.csv"

    parser = argparse.ArgumentParser(description="Generate S-curves from CSV parameters.")
    parser.add_argument("scurve_csv", nargs="?", type=str, default=default_csv_path, help="Path to S-curve CSV file")
    parser.add_argument("--query", type=str, default=None, help="Optional pandas query to filter data")
    parser.add_argument("--output", type=str, default=None, help="Optional path to save the generated S-curves as a CSV file.")
    return parser.parse_args()


def main() -> tuple[pd.DataFrame | None, pd.DataFrame]:
    """Main entry point for generating S-curves."""
    load_environment_from_dotenv()
    configure_loglevel(log_format=os.environ.get("LOG_FORMAT"))
    logger.debug(f"Starting {sys.executable} {__file__}")

    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    pd.set_option("display.multi_sparse", False)

    args = parse_arguments()
    csv = args.scurve_csv
    csv_file = pathlib.Path(csv)

    logger.info("Calculating all S-curves from {filename}", filename=csv_file)
    query = args.query

    s_curve_parameters = pd.read_csv(csv_file)

    df = generate_scurve_dataframe(filter_s_curve_parameters(query, s_curve_parameters))

    if args.output and args.output.endswith('.csv'):
        df.to_csv(args.output)
    if sys.flags.interactive:
        print("The results are available in `df`")
        return df, s_curve_parameters

    print(df[['share', 'share_acc']])
    return None, s_curve_parameters


if __name__ == "__main__":
    df, s_curve_parameters = main()
