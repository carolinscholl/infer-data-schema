import os
import logging
import re


def get_file_extension(fpath: str) -> str:
    """
    Get extension from a file path

    :param fpath: file path
    :return: extension
    """
    return os.path.splitext(fpath)[1]


def get_schema_fpath(fpath: str):
    """
    Edit a given file path of a json or csv by adding the suffix _schema-draft before the file extension

    :param fpath: data file path with extension
    :return: edited file path with _schema suffix before extension
    """
    try:
        f_path_no_ext = os.path.splitext(fpath)[0]
        extension = get_file_extension(fpath)
        if extension.endswith("csv"):
            extension += "s"  # .csvs extension for csv schema files
        updated_fpath = f_path_no_ext + "_schema-draft" + extension
        return updated_fpath
    except IOError as e:
        logging.error(f"Cannot add suffix to {fpath}: {e}.")


def replace_non_ascii_characters(str_to_edit: str, replacement: str = ".") -> str:
    """
    Replace all non-ASCII characters in a string with a replacement value

    :param str_to_edit: the string to edit
    :param replacement: replacement symbol
    :return: updated string
    """
    return re.sub('[^\x00-\x7F]', replacement, str_to_edit)
