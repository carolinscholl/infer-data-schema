import argparse
import logging

from infer_schema.infer_json_schema import InferJSONSchema
from infer_schema.infer_csv_schema import InferCSVSchema


def main():

    logging.basicConfig(format='(%(levelname)s) - %(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('data_fpath', type=str, help='path to data file for which to infer schema')
    parser.add_argument('--schema_fpath', type=str, required=False, help='optional path for output schema file',
                        default=None)
    args = parser.parse_args()
    data_fpath = args.data_fpath
    schema_fpath = args.schema_fpath

    if data_fpath.endswith("json"):
        InferJSONSchema(data_fpath).run(schema_fpath=schema_fpath)
    elif data_fpath.endswith("csv") or data_fpath.endswith("tsv"):
        InferCSVSchema(data_fpath).run(schema_fpath=schema_fpath)
    else:
        msg = f"File type for {data_fpath} not supported."\
              f" Only files with .json or .csv-extension are"\
              f" supported."
        logging.error(msg)


if __name__ == '__main__':
    main()
