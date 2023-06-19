import json
import logging
import os
from typing import Optional

from genson import SchemaBuilder
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from infer_schema.utils.utils import get_schema_fpath

JSONVersion = {
    6: "https://json-schema.org/draft-06/",  # draft_06
    7: "https://json-schema.org/draft-07/",  # draft_07
    2019: "https://json-schema.org/draft/2019-09/",  # draft_2019-09
    2020: "https://json-schema.org/draft/2020-12"  # draft_2020-12
}


class InferJSONSchema:
    def __init__(self, data_fpath: str, json_version: JSONVersion = JSONVersion[2020]) -> None:
        """
        Initialize variables

        :param data_fpath: path to json file containing the data
        :param json_version: version of the json standard
        """
        self.data_fpath = data_fpath
        self.json_version = json_version

    def create_schema_from_json(self) -> dict:
        """
        Infer the data schema from a json data file and return it as a dictionary. If a schema_path is provided, the
        inferred schema will be stored under the specified path.

        :return: inferred json schema as a dictionary
        """
        logging.info(f"Start json schema inference from file {self.data_fpath}")
        builder = SchemaBuilder(schema_uri=self.json_version)
        with open(self.data_fpath, 'r') as f:
            json_content = json.load(f)
            builder.add_object(json_content)
        schema = builder.to_schema()
        logging.info(f"Inferred json schema:\n {schema}\n")
        return schema

    def validate_json_schema(self, schema_path: str) -> bool:
        """
        Validate the data file against a schema.

        :param schema_path: path to json schema
        :return: True if validation passed, False otherwise
        """
        with open(self.data_fpath, 'r') as f:
            data_instance = json.load(f)
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        try:
            logging.info(f"Validate original data file {self.data_fpath} against inferred schema {schema_path}")
            logging.debug(validate(data_instance, schema))
            return True
        except ValidationError as e:
            logging.warning(f"Validation of file {self.data_fpath} against schema {schema_path} failed: {e}")
            return False

    def run(self, schema_fpath: Optional[str] = None) -> bool:
        """
        Run json schema inference, save inferred schema (same path as data file with extension _schema-draft.csvs) and
        validate it.

        :param schema_fpath: optional path for output schema, otherwise path will be data file name + _schema-draft.json
        :return: True if schema inference worked and data file could be validated with it, False otherwise
        """
        schema = self.create_schema_from_json()
        if schema_fpath in [None, ""]:
            schema_fpath = get_schema_fpath(self.data_fpath)
        os.makedirs(os.path.dirname(schema_fpath), exist_ok=True)
        try:
            with open(schema_fpath, "w") as f:
                json.dump(schema, f, indent=4)
            logging.info(f"Saved schema at {schema_fpath}.")
            return self.validate_json_schema(schema_fpath)
        except IOError as e:
            logging.warning(f"Cannot store schema at {schema_fpath}: {e}.")
            return False


if __name__ == '__main__':
    data_path = ""
    output_schema_path = ""
    json_v = JSONVersion[2020]
    InferJSONSchema(data_path, json_v).run()
