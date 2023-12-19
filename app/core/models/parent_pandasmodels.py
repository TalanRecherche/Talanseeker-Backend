"""Created by agarc at 26/10/2023
Features:
Parent class for all pandas dataframes models
Create the schemas in child classes as follows:

class MyModel(ParentPandasModel):
    # model columns, access using MyModel.name
    name = "name"
    surname = "surname"
    age = "age"
    income = "income"

    # class schema to enforce datatype and nullability
    schema = pa.DataFrameSchema({
        names: Column(list[str], nullable=True),
        surname: Column(str, nullable=True),
        age: Column(int, nullable=True),
        income: Column(float, nullable=True),
    })

The class methods are:
    - get_attributes(): return a list of the columns of the schema
    - validate_dataframe(df): check if the dataframe is valid according to the schema
    (check value type and columns name)
    - generate_dataframe(): generate an empty dataframe valid according to the schema
"""
import logging

import pandas as pd
import pandera as pa


class ParentPandasModel:
    """Parent class for all the models that are based on pandas"""

    # this will be overwritten by the child class
    schema = pa.DataFrameSchema({})

    @classmethod
    def get_attributes(cls) -> list[str]:
        """List columns of the schema"""
        return list(cls.schema.columns.keys())

    @classmethod
    def validate_dataframe(cls, df: pd.DataFrame) -> bool:
        """Check if the dataframe is valid according to the schema
        Args:
        df (pd.DataFrame): dataframe to validate

        Returns
        -------
        bool: True if all attributes are in the dataframe columns
            False otherwise
        """
        # TODO@antoine: add check for null values
        # TODO@antoine: add check for value type
        # TODO@antoine: add check for value format
        # TODO@antoine: add check for value length
        # TODO@antoine: add check for empty dataframe
        # TODO@antoine: for some execption can be the same
        try:
            cls.schema.validate(df)
            is_valid = True
        except pa.errors.SchemaError as e:
            is_valid = False
            log_string = f"DataFrame validation error: {e}"
            logging.error(log_string)
        return is_valid

    @classmethod
    def generate_dataframe(cls) -> pd.DataFrame:
        """Generate an empty dataframe with the columns of the schema and correct data
        types
        Args:
        df (pd.DataFrame): dataframe to generate attributes from

        Returns
        -------
        None
        """

        def _pandera_dtype_to_pandas_dtype(data_type: pa.dtypes) -> str:
            """Convert pandera data type to pandas data type.

            :param dtype: A pandera data type
            :return: A pandas data type
            """
            data_type = str(data_type)
            map_data_type = {
                "str": "object",
                "int64": "int64",
                "float": "float64",
                "bool": "boolean",
            }
            if data_type in map_data_type:
                return map_data_type[data_type]
            else:
                return "object"

        empty_data = {
            col_name: pd.Series([], dtype=_pandera_dtype_to_pandas_dtype(col.dtype))
            for col_name, col in cls.schema.columns.items()
        }
        empty_df = pd.DataFrame(empty_data)
        return empty_df
