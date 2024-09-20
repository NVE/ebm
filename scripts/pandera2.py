import pandas as pd
import pandera as pa

# Create a sample DataFrame with incorrect data types
data = {
    "column1": ["A", "B", "C", "D", 5],
    "column2": [1, 2, "three", 4, 'five']
}

df = pd.DataFrame(data)

# Define a Pandera schema with expected data types
schema = pa.DataFrameSchema({
    "column1": pa.Column(pa.String),
    "column2": pa.Column(pa.Int, coerce=True)
})

# Validate the DataFrame against the schema
try:
    validated_df = schema.validate(df, lazy=True)
except pa.errors.SchemaErrors as e:
    # Access the failure cases for each column
    failure_cases = e.failure_cases
    print(failure_cases[['index', 'column', 'failure_case']])
