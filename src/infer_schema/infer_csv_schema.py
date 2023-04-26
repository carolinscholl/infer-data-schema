import logging
import os

import pandas as pd
from omegaconf import OmegaConf

import src.utils.check_dtype as check_type
from src.utils.utils import get_schema_fpath, replace_non_ascii_characters
from typing import Optional


class InferCSVSchema:
    version = "version 1.2"  # version of csv standard
    literals_fpath = os.path.join(os.getcwd(), "src", "resources", "csv-type-literals.yml")

    def __init__(self, csv_path: str):
        """
        Read in csv file into pandas dataframe

        :param csv_path: path to csv file
        """
        self.csv_path = csv_path
        self.seperator = self.get_csv_separator(csv_path)
        self.literals = OmegaConf.load(self.literals_fpath)

        # read in everything as string to keep leading zeros
        self.df = pd.read_csv(csv_path, sep=self.seperator, dtype=str)

        # pandas treats many values as missing, the standard treats only "" as empty, so we have to detect any values
        # pandas treats as missing separately
        self.missing_symbols = list(pd._libs.parsers.STR_NA_VALUES)
        self.missing_symbols.remove(self.literals["MissingValue"])
        self.df_na = pd.read_csv(csv_path, sep=self.seperator, keep_default_na=False,
                                 na_values=self.literals["MissingValue"], dtype=str)
        # Read in as string to avoid automatic treatment of NaN symbols and type inference by pandas.
        # Only "" is a missing symbol according to the csv standard. It is displayed as "empty" in the schema.
        # It is checked if the remaining missing symbols from pandas library appear in the variable and if yes,
        # they are added as "or is(<missing symbol>), e.g. "or is(NA)" (see line 163)

    @staticmethod
    def get_csv_separator(csv_file_path: str) -> str:
        """
        Infer the used separator in the csv file

        :param csv_file_path: path to csv file
        :return: used separator as a character
        """
        reader = pd.read_csv(csv_file_path, sep=None, iterator=True, engine="python")  # infer delimiter first
        inferred_sep = reader._engine.data.dialect.delimiter
        reader.close()
        logging.debug(f"Inferred delimiter {inferred_sep} for csv file {csv_file_path}")
        return inferred_sep

    def create_schema_from_csv(self, use_regex_for_nums: bool = False, min_n_limits: int = 100) -> str:
        """
        Create the csv schema according to csv standard. Basic data types are inferred. Ranges are only inferred if
        at least min_n_limits non-missing values exist of a variable. The only limit that is inferred is that a
        variable is >=0.

        :param use_regex_for_nums: whether to use regex for numeric values (instead of range for ints and floats)
        :param min_n_limits: minimum number of total values for a variable to be considered positive
        :return: string containing the csv schema including line breaks
        """
        logging.info(f"Start csv schema inference from file {self.csv_path}")
        sep = "TAB" if self.seperator == "\t" else self.seperator
        schema = f"{self.version}\n" \
                 f"@totalColumns {int(len(self.df.columns))}\n"
        if self.seperator == "\t":
            schema += "@separator TAB\n"
        else:
            schema += f"@separator '{sep}'\n"
        for i_col, (col_name, var) in enumerate(self.df.items()):
            schema += f'"{col_name}": '
            if len(var.index) == 0:
                schema += "empty"
            # to check for the different missing values we have to use the dataframe with ignored missing values
            missings = []
            for m in self.missing_symbols:
                if m in self.df_na[col_name].to_list():
                    missings.append(m)
            if check_type.check_is_bool(var):
                schema += 'is("0") or is("1")'
            elif check_type.heuristic_check_categorical(var):
                cats = var.dropna().unique().tolist()
                if len(cats) == 1:  # constant value
                    if isinstance(cats[0], str) and not cats[0].isascii():
                        schema += f'regex("{replace_non_ascii_characters(cats[0])}")'
                    else:
                        schema += f'is("{cats[0]}")'
                else:
                    if check_type.check_is_numeric(var):
                        schema += 'any('
                        for i_cat, cat in enumerate(cats):
                            schema += f'"{cat}"'
                            if i_cat != len(cats) - 1:
                                schema += ','
                            else:
                                schema += ')'
                    elif check_type.check_regex(var, self.literals['String']):
                        ascii_strings, non_ascii_strings = [], []
                        for cat in cats:
                            if cat.isascii():
                                ascii_strings.append(cat)
                            else:
                                non_ascii_strings.append(cat)
                        if len(ascii_strings):
                            schema += 'any('
                            for i_cat, cat in enumerate(ascii_strings):
                                schema += f'"{cat}"'
                                if i_cat != len(ascii_strings) - 1:
                                    schema += ','
                                else:
                                    schema += ')'
                        if len(non_ascii_strings):
                            if not len(ascii_strings):
                                schema += f'regex("{replace_non_ascii_characters(non_ascii_strings[0])}")'
                                non_ascii_strings.pop(0)
                            for cat in non_ascii_strings:
                                schema += f' or regex("{replace_non_ascii_characters(cat)}")'
                    else:
                        schema += "any\n"
                        continue
            elif len(var.index) >= min_n_limits and check_type.check_is_numeric_positive(var):
                if check_type.check_is_positive_integer(var):
                    schema += "positiveInteger"
                else:
                    schema += "range(0, *)"
            elif check_type.check_is_numeric(var):
                if not use_regex_for_nums:
                    schema += "range(*, *)"
                else:
                    if check_type.check_is_integer(var):
                        schema += f'regex("{self.literals["Integer"]}")'
                    else:
                        schema += f'regex("{self.literals["Numeric"]}")'
            elif check_type.check_regex(var, self.literals['XsdDateTimeWithTimeZoneLiteral']):
                schema += "xDateTimeTz"
            elif check_type.check_regex(var, self.literals['XsdDateTimeLiteral']):
                schema += "xDateTime"
            elif check_type.check_regex(var, self.literals['XsdDateLiteral']):
                schema += "xDate"
            elif check_type.check_regex(var, self.literals['XsdTimeLiteral']):
                schema += "xTime"
            elif check_type.check_regex(var, self.literals['String']):
                str_var = var.dropna().to_list()
                if all([str_val.isalpha() for str_val in str_var]) \
                        and all([str_val.isupper() for str_val in str_var]) \
                        and all([str_val.isupper() for str_val in missings]):
                    schema += "upperCase "
                elif all([str_val.isalpha() for str_val in str_var]) \
                        and all([str_val.islower() for str_val in str_var]) \
                        and all([str_val.islower() for str_val in missings]):
                    schema += "lowerCase "
                if all([len(str_val) == 1 for str_val in str_var]):
                    schema += "length(1)"  # character
                else:
                    schema += "length(1, *)"
            else:
                schema += "any\n"
                continue
            if len(missings):  # append alternative missing values
                for i_m in missings:
                    schema += f' or is("{i_m}")'
            if any(self.df_na[col_name].isna()):
                schema += " or empty"
            if i_col < len(self.df.columns)-1:
                schema += "\n"
        logging.info(f"Inferred csv schema:\n\n{schema}\n")
        return schema

    def run(self, schema_fpath: Optional[str] = None) -> bool:
        """
        Run csv schema inference and save inferred schema (same path as data file with extension _schema-draft.csvs).

        :param schema_fpath: optional path for output schema, otherwise path will be data file name + _schema-draft.csvs
        :return: True if schema inference worked and data file could be validated with it, False otherwise
        """
        schema = self.create_schema_from_csv()
        if schema_fpath in [None, ""]:
            schema_fpath = get_schema_fpath(self.csv_path)
        os.makedirs(os.path.dirname(schema_fpath), exist_ok=True)
        try:
            with open(schema_fpath, 'w') as f:
                f.write(schema)
            logging.info(f"Saved inferred data schema at {schema_fpath}.")
            return True
        except IOError as e:
            logging.warning(f"Cannot store data schema at {schema_fpath}: {e}.")
            return False


if __name__ == '__main__':
    path_csv = ""
    out_path = None
    data_schema = InferCSVSchema(path_csv).run()
