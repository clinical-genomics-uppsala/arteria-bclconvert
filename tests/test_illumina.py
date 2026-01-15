# This file has been modified from the https://github.com/arteria-project/arteria-bcl2fastq repo
# bcl2fastq/tests/test_illumina.py
import unittest
import os
from io import StringIO

from bclconvert.lib.illumina import *



class TestSamplesheet(unittest.TestCase):
    test_dir = os.path.dirname(os.path.realpath(__file__))
    samplesheet_file = test_dir + "/sampledata/new_samplesheet_example.csv"
    tiny_dummy_samplesheet_string = """
,,,,,,,,
[Data],,,,,,,,
Lane,Sample_ID,Sample_Name,Sample_Plate,Sample_Well,I7_Index_ID,index,Sample_Project,Description
1,1,1,,,,CAGATC,Dummy-Project,FRAGMENT_SIZE:387;FRAGMENT_LOWER:180;FRAGMENT_UPPER:580;LIBRARY_NAME:SX444_1
1,2,2,,,,ACTTGA,Dummy-Project,FRAGMENT_SIZE:387;FRAGMENT_LOWER:180;FRAGMENT_UPPER:580;LIBRARY_NAME:SX444_2
"""

    expected_samples = [
        SampleRow(lane="1", sample_id="1", sample_name="1",
                  sample_well="", sample_plate="",
                  index1="CAGATC", sample_project="Dummy-Project",
                  description="FRAGMENT_SIZE:387;FRAGMENT_LOWER:180;FRAGMENT_UPPER:580;LIBRARY_NAME:SX444_1"),
        SampleRow(lane="1", sample_id="2", sample_name="2",
                  sample_well="", sample_plate="",
                  index1="ACTTGA", sample_project="Dummy-Project",
                  description="FRAGMENT_SIZE:387;FRAGMENT_LOWER:180;FRAGMENT_UPPER:580;LIBRARY_NAME:SX444_2")
    ]

    def test_samplesheet(self):
        # TODO This can probably improved by using mocks in some smart way
        # TODO but right it doesn't feel like it's worth it. /JD 20150813
        result = Samplesheet(TestSamplesheet.samplesheet_file)
        self.assertEqual(len(result.samples), 8)

    def test__read_samples(self):
        result = Samplesheet._read_samples(StringIO(TestSamplesheet.tiny_dummy_samplesheet_string))
        self.assertEqual(result, TestSamplesheet.expected_samples)

    def test_samplerow_defaults(self):
        samplerow = SampleRow(sample_id="1", sample_name="1",
                              index1="CAGATC", sample_project="Dummy-Project")
        self.assertEqual(samplerow.lane, 1)
        self.assertEqual(samplerow.sample_plate, None)
        self.assertEqual(samplerow.sample_well, None)
        self.assertEqual(samplerow.index2, None)
        self.assertEqual(samplerow.description, None)


class TestSamplesheetCloudSettings(unittest.TestCase):
    test_dir = os.path.dirname(os.path.realpath(__file__))
    samplesheet_file = test_dir + "/sampledata/new_samplesheet_example_cloud.csv"

    expected_samples = [
        SampleRow(lane="1", sample_id="1", sample_name="1",
                  sample_well="", sample_plate="",
                  index1="CAGATC", sample_project="Dummy-Project",
                  description="FRAGMENT_SIZE:387;FRAGMENT_LOWER:180;FRAGMENT_UPPER:580;LIBRARY_NAME:SX444_1"),
        SampleRow(lane="1", sample_id="2", sample_name="2",
                  sample_well="", sample_plate="",
                  index1="ACTTGA", sample_project="Dummy-Project",
                  description="FRAGMENT_SIZE:387;FRAGMENT_LOWER:180;FRAGMENT_UPPER:580;LIBRARY_NAME:SX444_2")
    ]

    def test_samplesheet(self):
        # TODO This can probably improved by using mocks in some smart way
        # TODO but right it doesn't feel like it's worth it. /JD 20150813
        result = Samplesheet(TestSamplesheetCloudSettings.samplesheet_file)
        self.assertEqual(len(result.samples), 15)