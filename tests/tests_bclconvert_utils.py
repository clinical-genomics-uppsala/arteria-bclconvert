# This file has been modified from the https://github.com/arteria-project/arteria-bcl2fastq repo
# bcl2fastq/tests/test_bcl2fastq_utils_logs.py

import unittest
from mock import patch
import tempfile
import os

from bclconvert.lib.bclconvert_utils import *
from bclconvert.lib.illumina import Samplesheet
from .test_utils import TestUtils, DummyConfig


DUMMY_CONFIG = DummyConfig()

class TestBclConvertConfig(unittest.TestCase):

    test_dir = os.path.dirname(os.path.realpath(__file__))
    samplesheet_file = test_dir + "/sampledata/new_samplesheet_example.csv"
    samplesheet_with_no_tag = test_dir + "/sampledata/no_tag_samplesheet_example.csv"
    dummy_config = DummyConfig()

    def test_get_bclconvert_version_from_run_parameters(self):
        runfolder = TestBclConvertConfig.test_dir + "/sampledata/HiSeq-samples/2014-02_13_average_run"
        version = BclConvertConfig.get_bclconvert_version_from_run_parameters(runfolder, self.dummy_config)
        self.assertEqual(version, "4.0.3")

    def test_is_single_read_true(self):
        runfolder = TestBclConvertConfig.test_dir + "/sampledata/HiSeq-samples/2014-02_13_average_run"
        self.assertFalse(BclConvertConfig.is_single_read(runfolder))

    def test_is_single_read_false(self):
        runfolder = TestBclConvertConfig.test_dir + "/sampledata/MiSeq-samples/2014-02_11_50kit_single_read"
        self.assertTrue(BclConvertConfig.is_single_read(runfolder))

    def test_get_length_of_indexes(self):
        runfolder = TestBclConvertConfig.test_dir + "/sampledata/HiSeq-samples/2014-02_13_average_run"
        index_and_length = BclConvertConfig.get_length_of_indexes(runfolder)
        self.assertEqual(index_and_length, {2: 7})

    def test_write_samplesheet(self):
        f = tempfile.mktemp()
        BclConvertConfig.write_samplesheet(TestUtils.DUMMY_SAMPLESHEET_STRING, f)
        with open(f, "r") as my_file:
            content = my_file.read()
            self.assertEqual(content, TestUtils.DUMMY_SAMPLESHEET_STRING)
        os.remove(f)

    def test_samplesheet_gets_written(self):
        with patch.object(BclConvertConfig, "write_samplesheet") as ws:
            # If we provide a samplesheet to the config this should be written.
            # In this case this write call is mocked away to make testing easier,
            # but the write it self should be trivial.
            config = BclConvertConfig(
                general_config = DUMMY_CONFIG,
                bclconvert_version = "4.0.3",
                runfolder_input = "test/runfolder",
                output = "test/output",
                samplesheet=TestUtils.DUMMY_SAMPLESHEET_STRING)

            ws.assert_called_once_with(TestUtils.DUMMY_SAMPLESHEET_STRING, config.samplesheet_file)

    def test_get_bases_mask_per_lane_from_samplesheet(self):
        mock_read_index_lengths = {2: 9, 3: 9}
        expected_bases_mask = {1: "y*,i8n*,i8n*,y*",
                               2: "y*,i6n*,n*,y*",
                               3: "y*,i6n*,n*,y*",
                               4: "y*,i7n*,n*,y*",
                               5: "y*,i7n*,n*,y*",
                               6: "y*,i7n*,n*,y*",
                               7: "y*,i7n*,n*,y*",
                               8: "y*,i7n*,n*,y*",
                               }
        samplesheet = Samplesheet(TestBclConvertConfig.samplesheet_file)
        actual_bases_mask = BclConvertConfig. \
            get_bases_mask_per_lane_from_samplesheet(samplesheet, mock_read_index_lengths, False)
        self.assertEqual(expected_bases_mask, actual_bases_mask)

    def test_get_bases_mask_per_lane_from_samplesheet_single_read(self):
        mock_read_index_lengths = {2: 9, 3: 9}
        expected_bases_mask = {1: "y*,i8n*,i8n*",
                               2: "y*,i6n*,n*",
                               3: "y*,i6n*,n*",
                               4: "y*,i7n*,n*",
                               5: "y*,i7n*,n*",
                               6: "y*,i7n*,n*",
                               7: "y*,i7n*,n*",
                               8: "y*,i7n*,n*",
                               }
        samplesheet = Samplesheet(TestBclConvertConfig.samplesheet_file)
        actual_bases_mask = BclConvertConfig. \
            get_bases_mask_per_lane_from_samplesheet(samplesheet, mock_read_index_lengths, True)
        self.assertEqual(expected_bases_mask, actual_bases_mask)

    def test_get_bases_mask_per_lane_from_samplesheet_invalid_length_combo(self):
        # These are to short compared to the length indicated in the samplesheet
        mock_read_index_lengths = {2: 4, 3: 4}
        samplesheet = Samplesheet(TestBclConvertConfig.samplesheet_file)

        with self.assertRaises(ArteriaUsageException):
            BclConvertConfig. \
                get_bases_mask_per_lane_from_samplesheet(samplesheet, mock_read_index_lengths, False)

    def test_get_bases_mask_per_lane_from_samplesheet_no_tag(self):
        # If we don't have tag for one lane in the samplesheet.
        mock_read_index_lengths = {2: 6}
        expected_bases_mask = {1: "y*,n*,y*",
                               2: "y*,n*,y*",
                               3: "y*,i6,y*",
                               4: "y*,i6,y*",
                               5: "y*,i6,y*",
                               6: "y*,i6,y*",
                               7: "y*,n*,y*",
                               8: "y*,n*,y*",
                               }
        samplesheet = Samplesheet(TestBclConvertConfig.samplesheet_with_no_tag)
        actual_bases_mask = BclConvertConfig. \
            get_bases_mask_per_lane_from_samplesheet(samplesheet, mock_read_index_lengths, False)
        self.assertEqual(expected_bases_mask, actual_bases_mask)


class TestBCLConvertRunnerFactory(unittest.TestCase):

    dummy_config = DummyConfig()

    def test_create_bcl2fastq1x_runner(self):
        config = BclConvertConfig(
            general_config = DUMMY_CONFIG,
            bclconvert_version = "4.0.3",
            runfolder_input = "test/runfolder",
            output = "test/output")

        factory = BclConvertRunnerFactory(self.dummy_config)
        runner = factory.create_bcl2fastq_runner(config)
        self.assertIsInstance(runner, BclConvertRunner)

    def test_create_bcl2fastq2x_runner(self):
        config = BclConvertConfig(
            general_config = DUMMY_CONFIG,
            bclconvert_version = "4.0.3",
            runfolder_input = "test/runfolder",
            output = "test/output")

        factory = BclConvertRunnerFactory(self.dummy_config)
        runner = factory.create_bcl2fastq_runner(config)
        self.assertIsInstance(runner, BCLConvertRunner, msg="runner is: " + str(runner))

    def test_create_invalid_version_runner(self):
        config = BclConvertConfig(
            general_config = DUMMY_CONFIG,
            bclconvert_version = "1.7",
            runfolder_input = "test/runfolder",
            output = "test/output")

        factory = BclConvertRunnerFactory(self.dummy_config)
        with self.assertRaises(LookupError):
            factory.create_bcl2fastq_runner(config)


class TestConvertRunner(unittest.TestCase):
    def test_construct_command(self):

        config = BclConvertConfig(
            general_config = DUMMY_CONFIG,
            bclconvert_version = "4.0.3",
            runfolder_input = "test/runfolder",
            output = "test/output",
            barcode_mismatches = "2",
            tiles="s1,s2,s3",
            use_base_mask="--use-bases-mask y*,i6,i6,y* --use-bases-mask 1:y*,i5,i5,y*",
            additional_args="--my-best-arg 1 --my-best-arg 2")

        runner = BCLConvertRunner(config, "/bcl/binary/path")
        command = runner.construct_command()
        expected_command = "/bcl/binary/path --input-dir test/runfolder/Data/Intensities/BaseCalls " \
                           "--output-dir test/output " \
                           "--sample-sheet test/runfolder/SampleSheet.csv " \
                           "--barcode-mismatches 2 " \
                           "--tiles s1,s2,s3 " \
                           "--use-bases-mask y*,i6,i6,y* --use-bases-mask 1:y*,i5,i5,y* " \
                           "--my-best-arg 1 --my-best-arg 2"
        self.assertEqual(command, expected_command)

class TestBCLConvertRunner(unittest.TestCase):

    config = BclConvertConfig(
        general_config = DUMMY_CONFIG,
        bclconvert_version = "4.0.3",
        runfolder_input = "test/runfolder",
        output = "test/output",
        barcode_mismatches = "2",
        tiles="s1,s2,s3",
        use_base_mask="--use-bases-mask y*,i6,i6,y* --use-bases-mask 1:y*,i5,i5,y*",
        additional_args="--my-best-arg 1 --my-best-arg 2")

    class DummyBCLConvertRunner(BclConvertRunner):
        def __init__(self, config, binary, dummy_command):
            self.dummy_command = dummy_command
            BclConvertRunner.__init__(self, config, binary)

        def construct_command(self):
            return self.dummy_command

    def test_symlink_output_to_unaligned(self):
        with patch.object(os, 'symlink', return_value=None) as m:
            dummy_runner = self.DummyBCLConvertRunner(TestBCLConvertRunner.config, None, None)
            dummy_runner.symlink_output_to_unaligned()
            m.assert_called_with(
                TestBCLConvertRunner.config.output,
                TestBCLConvertRunner.config.runfolder_input + "/Unaligned")

        # Check that trying to create an already existing softlink doesn't break the function.
        # Please note that the second side effect is None, which means that the second time th
        # mock is called it will work.
        with patch.object(os, 'remove', return_value=None) as r, \
             patch.object(os, 'symlink', side_effect=[OSError(17, "message"), None]) as m:
            dummy_runner = self.DummyBCLConvertRunner(TestBCLConvertRunner.config, None, None)
            dummy_runner.symlink_output_to_unaligned()
            m.assert_called_with(TestBCLConvertRunner.config.output,
                                 TestBCLConvertRunner.config.runfolder_input + "/Unaligned")
            r.assert_called_with(TestBCLConvertRunner.config.runfolder_input + "/Unaligned")

        # While any other error should
        with patch.object(os, 'symlink', side_effect=OSError(1, "message")) as m:
            with self.assertRaises(OSError):
                dummy_runner = self.DummyBCLConvertRunner(TestBCLConvertRunner.config, None, None)
                dummy_runner.symlink_output_to_unaligned()
                m.assert_called_with(TestBCLConvertRunner.config.output,
                                     TestBCLConvertRunner.config.runfolder_input + "/Unaligned")


class TestLaneParsing(unittest.TestCase):
    """Test lane specification parsing to tiles regex"""

    def test_parse_single_lane(self):
        result = BclConvertConfig.parse_lanes_to_tiles_regex("1")
        self.assertEqual(result, "s_1")

    def test_parse_multiple_lanes(self):
        result = BclConvertConfig.parse_lanes_to_tiles_regex("13")
        self.assertEqual(result, "s_[13]")

    def test_parse_lane_range(self):
        result = BclConvertConfig.parse_lanes_to_tiles_regex("2-6")
        self.assertEqual(result, "s_[2-6]")

    def test_parse_full_range(self):
        result = BclConvertConfig.parse_lanes_to_tiles_regex("1-8")
        self.assertEqual(result, "s_[1-8]")

    def test_parse_mixed_lanes_and_range(self):
        result = BclConvertConfig.parse_lanes_to_tiles_regex("13-5")
        self.assertEqual(result, "s_[13-5]")

    def test_parse_complex_pattern(self):
        result = BclConvertConfig.parse_lanes_to_tiles_regex("1-46-7")
        self.assertEqual(result, "s_[1-46-7]")

    def test_invalid_format_letters(self):
        with self.assertRaises(ArteriaUsageException):
            BclConvertConfig.parse_lanes_to_tiles_regex("abc")

    def test_invalid_format_special_chars(self):
        with self.assertRaises(ArteriaUsageException):
            BclConvertConfig.parse_lanes_to_tiles_regex("1,3")

    def test_invalid_range_reversed(self):
        with self.assertRaises(ArteriaUsageException):
            BclConvertConfig.parse_lanes_to_tiles_regex("6-2")

    def test_invalid_range_equal(self):
        with self.assertRaises(ArteriaUsageException):
            BclConvertConfig.parse_lanes_to_tiles_regex("3-3")

    def test_invalid_lane_number_zero(self):
        with self.assertRaises(ArteriaUsageException):
            BclConvertConfig.parse_lanes_to_tiles_regex("0")

    def test_invalid_lane_number_too_high(self):
        with self.assertRaises(ArteriaUsageException):
            BclConvertConfig.parse_lanes_to_tiles_regex("9")

    def test_empty_string(self):
        with self.assertRaises(ArteriaUsageException):
            BclConvertConfig.parse_lanes_to_tiles_regex("")

    def test_none_value(self):
        with self.assertRaises(ArteriaUsageException):
            BclConvertConfig.parse_lanes_to_tiles_regex(None)

    def test_starts_with_hyphen(self):
        with self.assertRaises(ArteriaUsageException):
            BclConvertConfig.parse_lanes_to_tiles_regex("-13")

    def test_ends_with_hyphen(self):
        with self.assertRaises(ArteriaUsageException):
            BclConvertConfig.parse_lanes_to_tiles_regex("13-")

    def test_consecutive_hyphens(self):
        with self.assertRaises(ArteriaUsageException):
            BclConvertConfig.parse_lanes_to_tiles_regex("1--3")
