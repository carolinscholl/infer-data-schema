"""
Helper methods to check variables for data types. Pandas data type inference does not work well in case of missing
values because NaN are interpreted as floats.
"""
import math
import pandas as pd
import re
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)


def check_is_integer(var: pd.Series) -> bool:
    """
    Check whether all data points of a variable in a pandas dataframe are of integer type

    :param var: pandas series of the variable
    :return: True if the variable is integer
    """
    if not check_is_numeric(var):
        return False
    else:
        try:
            var.dropna().astype("int")
            return True
        except ValueError:
            return False


def check_is_positive_integer(var: pd.Series) -> bool:
    """
    Check if all data points of a variable in a pandas dataframe are integers >= 0 by casting them to string.

    :param var: pandas series of the variable
    :return: True if the variable only contains integers >=0
    """
    if not check_is_integer(var):
        return False
    else:
        var = var.dropna().astype("int")
        values_list = var.to_list()
        return all([str(x).isdigit() for x in values_list])


def check_is_float(var: pd.Series, allow_integers: bool = True) -> bool:
    """
    Check whether data points of a variable in a pandas dataframe are of float type. The parameter allow_integers
    specifies whether values that are encoded as integers (e.g. a=1) are also accepted as floats. In that case, it
    is only checked whether the variable is numeric. NaN values are ignored

    :param var: pandas series of the variable
    :param allow_integers: whether values encoded as integers are also accepted as floats
    :return: True if the variable is float
    """
    is_numeric = check_is_numeric(var)
    if allow_integers:
        return is_numeric
    elif is_numeric:
        var = var.dropna().astype("float")
        values_list = var.to_list()
        return all([isinstance(x, float) for x in values_list])
    else:
        return False


def check_is_numeric(var: pd.Series):
    """
    Check whether all data points of a variable in a pandas dataframe are numeric.

    :param var: pandas series of the variable
    :return: True if the variable is numeric
    """
    try:
        var = var.dropna().astype("float")
        return pd.api.types.is_numeric_dtype(var)
    except ValueError:
        return False


def check_is_numeric_positive(var: pd.Series) -> bool:
    """
    Check if all non-missing values of a numeric variable are >=0.

    :param var: pandas series of the variable
    :return: True if the variable contains only values >=0
    """
    if not check_is_numeric(var):
        return False
    else:
        var = var.dropna().astype("float")
        values_list = var.to_list()
        return all([x >= 0 for x in values_list])


def check_is_bool(var: pd.Series):
    """
    Check whether all data points of a variable in a pandas dataframe are boolean by casting the non-missing values
    to boolean and comparing it against original variable.

    :param var: pandas series of the variable
    :return: True if the variable is boolean
    """
    values_list = var.dropna().to_list()
    try:
        cast_to_int = [int(i) for i in values_list]
        cast_to_bool = [bool(i) for i in cast_to_int]
        return cast_to_bool == cast_to_int
    except ValueError:
        return False


def check_regex(var: pd.Series, expression: str) -> bool:
    """
    Check whether a variable from a pandas dataframe is in accordance with specified regular expression

    :param var: pandas series of the variable
    :param expression: regular expression written as string
    :return: True if all values meet the regular expression condition
    """
    values_list = var.dropna().to_list()
    return all([bool(re.match(expression, x)) for x in values_list])


def heuristic_check_categorical(var: pd.Series, n_max_cats: int = 25, thr_min: float = 0.8, thr_max: float = 0.97,
                                forbid_float_categories: bool = False) \
        -> bool:
    """
    Check whether the variable might be categorical. Note: this can never be certain. First, it is checked whether
    the number of unique values lies below the maximum number of categories (n_max_cats). If that is the case,
    another heuristic is used to identify categorical variables. The algorithm proposed by
    https://jeffreymorgan.io/articles/identifying-categorical-data/ was adapted by computing an adaptive threshold.
    The threshold refers to the allowed ratio of number of unique values vs. total number of values to be seen as not
    categorical. This threshold is adaptively computed such that it is higher for variables with higher n.

    :param var: pandas series of the variable
    :param n_max_cats: maximum number of allowed categories
    :param thr_min: minimum threshold
    :param thr_max: maximum threshold
    :param forbid_float_categories: whether floating point number as valid category identifiers
    :return: True if variable is assumed to be categorical
    """
    var = var.dropna()
    if forbid_float_categories and check_is_float(var):
        return False
    n_unique_values = var.nunique()
    if n_unique_values > n_max_cats:
        return False
    thr = 1 - math.pow(1.5, math.log2(len(var))) / len(var)
    thr = thr_min if thr < thr_min else thr
    thr = thr_max if thr > thr_max else thr
    diff_total_unique = len(var) - n_unique_values
    ratio_total_unique = diff_total_unique / len(var)
    if ratio_total_unique > thr:
        return True
    else:
        return False
