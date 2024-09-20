import pandera as pa
from pandera import Column, DataFrameSchema, Check

schema = DataFrameSchema({
    "column1": Column(int, checks=[
        Check(lambda s: s > 0, title="positive_values_check")
    ])
})

# Example DataFrame
import pandas as pd
df = pd.DataFrame({"column1": [1, -1, 3]})

# Validate the DataFrame
try:
    schema.validate(df)
except pa.errors.SchemaError as e:
    print(e)
    print(e.failure_cases)