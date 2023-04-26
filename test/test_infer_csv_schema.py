import os
import shutil
import tempfile
import unittest

from src.infer_schema.infer_csv_schema import InferCSVSchema


class InferCsvSchemaTest(unittest.TestCase):
    """Tests for inferring a schema from a csv file"""

    test_data_file = os.path.join(os.getcwd(), "test", "test-data", "dummy.csv")
    gt_schema = os.path.join(os.getcwd(), "test", "test-data", "gt_dummy-schema.csvs")

    def setUp(self) -> None:
        self.tmp_dir = os.path.join(tempfile.gettempdir(), InferCsvSchemaTest.__name__)
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)
        else:
            shutil.rmtree(self.tmp_dir)
            os.makedirs(self.tmp_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir)

    def test_infer_csv_schema(self):
        schema = InferCSVSchema(self.test_data_file).create_schema_from_csv(min_n_limits=1)
        with open(self.gt_schema, "r") as f:
            gt_schema = f.read()
        assert schema == gt_schema
