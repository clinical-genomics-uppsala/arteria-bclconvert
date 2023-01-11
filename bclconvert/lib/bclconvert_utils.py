import subprocess
import os
import errno
from itertools import groupby
import logging
import shutil
import time


import xmltodict


from arteria.exceptions import ArteriaUsageException
from bclconvert.lib.illumina import Samplesheet

log = logging.getLogger(__name__)


class BclConvertConfig:
    """
    Container for configurations for bclconvert.
    Should handle setting up sensible defaults for
    values which have to be set.
    """
    def __init__(self,
                 general_config,
                 bclconvert_version,
                 runfolder_input,
                 output,
                 samplesheet=None,
                 barcode_mismatches=None,
                 tiles=None,
                 exclude_tiles=None,
                 use_base_mask=None,
                 bcl_only_lane=None,
                 create_indexes=False,
                 bcl_num_parallel_tiles=None,
                 bcl_num_conversion_threads=None,
                 bcl_num_compression_threads=None,
                 bcl_num_decompression_threads=None,
                 additional_args=None):
        """
        Instantiate BclConvertConfig
        :param general_config: a dict containing general configuration.
                               Typlically loaded from arteria-core ConfigurationService
        :param bclconvert_version: version of bclconvert to run
        :param runfolder_input: the path to the runfolder to run bclconvert on
        :param output: where the output of bclconvert should be placed
        :param samplesheet: a samplesheet as a raw string - if none is provided the samplesheet in the
                            runfolder will be used. If it is specified this provided string will be
                            written to a file and passed to bclconvert.
        :param barcode_mismatches: how many mismatches to allow in tag.
        :param tiles: tiles to include when running bclconvert
        :param exclude_tiles: tiles to exclude when running bclconvert
        :param use_base_mask: base mask to use
        :param bcl_only_lane: only convert specified lane
        :param create_indexes: Create fastq files for indexes
        :bcl_num_parallel_tiles number of tiles to process at the same time, default 1
        :bcl_num_conversion_thread number of conversion threads, default 1
        :bcl_num_compression_threads number of compression threads, default 1
        :bcl_num_decompression_threads number of decompression threads, default 1
        :param additional_args: this can be used to pass any other arguments to bclconvert
        """

        self.general_config = general_config

        self.runfolder_input = runfolder_input

        if not samplesheet:
            self.samplesheet_file = runfolder_input + "/SampleSheet.csv"
        else:
            log.debug("Got a new samplesheet. Will use that instead of the one found in the runfolder.")
            new_samplesheet_file = runfolder_input + "/SampleSheet.csv"

            if os.path.exists(new_samplesheet_file):
                BclConvertConfig.copy_old_samplesheet(new_samplesheet_file)

            BclConvertConfig.write_samplesheet(samplesheet, new_samplesheet_file)
            self.samplesheet_file = new_samplesheet_file

        if bclconvert_version:
            self.bclconvert_version = bclconvert_version
        else:
            self.bclconvert_version = BclConvertConfig. \
                get_bclconvert_version_from_run_parameters(runfolder_input, general_config)

        if output:
            self.output = output
        else:
            output_base = general_config["default_output_path"]
            runfolder_base_name = os.path.basename(runfolder_input)
            self.output = os.path.join(output_base, runfolder_base_name)
            if not os.path.exists(self.output):
                os.mkdir(self.output)

        self.barcode_mismatches = barcode_mismatches
        self.exclude_tiles = exclude_tiles
        self.bcl_only_lane = bcl_only_lane
        self.tiles = tiles

        # TODO Ensure that this is included in any user facing documentation.
        # Note that for the base mask the "--use-bases-mask" must be included in the
        # commandline passed. E.g. "--use-bases-mask 1:y*,6i,6i, y* --use-bases-mask y*,6i,6i, y* "
        self.use_base_mask = use_base_mask
        self.additional_args = additional_args
        self.create_indexes = create_indexes

        # Nbr of cores to use will default to the number of cpus on the system.
        import multiprocessing
        self.nbr_of_cores = multiprocessing.cpu_count()

        self.bcl_sampleproject_subdirectories = general_config["bcl_sampleproject_subdirectories"]
        self.sample_name_column_enabled = general_config["sample_name_column_enabled"]
        self.strict_mode = general_config["strict_mode"]
        self.fastq_gzip_compression_level = general_config["fastq_gzip_compression_level"]
        self.no_lane_splitting = general_config["no_lane_splitting"]
        self.num_unknown_barcodes_reported = general_config["num_unknown_barcodes_reported"]
        self.output_legacy_stats = general_config["output_legacy_stats"]

        if bcl_num_parallel_tiles:
            self.bcl_num_parallel_tiles = bcl_num_parallel_tiles
        else:
            self.bcl_num_parallel_tiles = general_config['bcl_num_parallel_tiles']

        if bcl_num_conversion_threads:
            self.bcl_num_conversion_threads = bcl_num_conversion_threads
        else:
            self.bcl_num_conversion_threads = general_config["bcl_num_conversion_threads"]

        if bcl_num_compression_threads:
            self.bcl_num_compression_threads = bcl_num_compression_threads
        else:
            self.bcl_num_compression_threads = general_config["bcl_num_compression_threads"]

        if bcl_num_decompression_threads:
            self.bcl_num_decompression_threads = bcl_num_decompression_threads
        else:
            self.bcl_num_decompression_threads = general_config["bcl_num_decompression_threads"]

        threads_requested = self.bcl_num_conversion_threads + self.bcl_num_compression_threads + self.bcl_num_decompression_threads
        if self.nbr_of_cores < threads_requested:
            logging.warning(f"bcl-convert will use {threads_requested} threads, {self.nbr_of_cores} exist!")

    @staticmethod
    def copy_old_samplesheet(new_samplesheet_file):
        new_path_for_old_samplesheet = new_samplesheet_file + time.strftime("%Y%m%d-%H%M%S")
        log.debug("Original samplesheet: {} copied to: {}. ".
                  format(new_samplesheet_file, new_path_for_old_samplesheet))
        shutil.copy(new_samplesheet_file,  new_path_for_old_samplesheet)

    @staticmethod
    def write_samplesheet(samplesheet_string, new_samplesheet_file):
        with open(new_samplesheet_file, "w") as f:
            f.write(samplesheet_string)

    @staticmethod
    def runinfo_as_dict(runfolder):
        runinfo_path = os.path.join(runfolder, "RunInfo.xml")
        with open(runinfo_path) as f:
            return xmltodict.parse(f.read())

    @staticmethod
    def get_bclconvert_version_from_run_parameters(runfolder, config):
        """
        Guess which bclconvert version to use based on the machine type
        specified in the runfolder meta data, and the corresponding
        mappings in the config file.
        :param runfolder: to get bclconvert version to use for
        :param config: to use matching machine type to bclconvert versions
        :return the version of bclconvert to use.
        """

        run_info = BclConvertConfig.runinfo_as_dict(runfolder)
        instrument_name = run_info["RunInfo"]["Run"]["Instrument"]

        machine_type_mappings = {"M": "MiSeq",
                                 "D": "HiSeq 2500",
                                 "SN": "HiSeq 2000",
                                 "ST": "HiSeq X",
                                 "A": "NovaSeq",
                                 "NS": "NextSeq 500",
                                 "NB": "NextSeq 500 D",
                                 "NDX": "NextSeq 550 DX",
                                 "K": "HiSeq 4000",
                                 "FS": "ISeq 100"}

        for key, value in machine_type_mappings.items():
            if instrument_name.startswith(key):
                return config["machine_type"][value]["bclconvert_version"]

    @staticmethod
    def get_length_of_indexes(runfolder):
        """
        Will parse runfolder meta data to find the length of the index reads.
        :param runfolder: to get the length of the index reads from.
        :return: a dict with the read number as key and the length of each index as value e.g.:
                 {2: 7, 3: 8}
        """

        run_info = BclConvertConfig.runinfo_as_dict(runfolder)
        reads = run_info["RunInfo"]["Run"]["Reads"]["Read"]

        index_lengths = {}
        for read in reads:
            if read['@IsIndexedRead'] == 'Y':
                index_lengths[int(read['@Number'])] = int(read['@NumCycles'])
        return index_lengths

    @staticmethod
    def is_single_read(runfolder):
        run_info = BclConvertConfig.runinfo_as_dict(runfolder)
        reads = run_info["RunInfo"]["Run"]["Reads"]["Read"]

        nbr_of_reads = len(list(filter(lambda x: not x["@IsIndexedRead"] == 'Y', reads)))
        return nbr_of_reads < 2

    @staticmethod
    def get_bases_mask_per_lane_from_samplesheet(samplesheet, index_lengths, is_single_read):
        """
        Create a bases-mask string per lane for based on the length of the index in the
        provided samplesheet. This assumes that all indexes within a lane have
        the same length.

        If the length read on the machine (as specified in `index_lengths`) is longer
        than the index length specified samplesheet, the base mask will be set to
        mask any extra bases.

        :param samplesheet: samplesheet to fetch the index lengths from
        :param index_lengths: dict of index lengths (e.g. "{1: 7, 2: 8}"),
        normally parsed from run meta data.
        :param is_single_read: True if this is a single read run, else false.
        :return a dict of the lane and base mask to use, e.g.:
                 { 1:"y*,i7n*,i7n*,y*" , 2:"y*,i5,n*,y*  [etc] }
        """

        def build_index_string(length_tuple):
            """
            Builds the index mask string
            :param length_tuple: a tuple of the length of the index in the samplesheet and in the read, e.g. (3, 5)
            :return: a index string, e.g. "i5n*" or "n*" or "i3", depending on the situation.
            """
            length_of_index_in_samplesheet = length_tuple[0]
            length_of_index_read = length_tuple[1]
            difference = length_of_index_read - length_of_index_in_samplesheet

            if not difference >= 0:
                raise ArteriaUsageException("Sample sheet indicates that index is "
                                            "longer than what was read by the sequencer!")

            if length_of_index_in_samplesheet == 0:
                # If there is no index in the samplesheet, ignore it in the base-mask
                return "n*"

            if difference > 0:
                # Pad the end if there is a difference here.
                return "i" + str(length_of_index_in_samplesheet) + "n*"
            else:
                return "i" + str(length_of_index_in_samplesheet)

        def construct_base_mask(samplesheet_idx_list):
            """
            Will construct the base mask.
            :param samplesheet_idx_list: A list of the indexes in the samplesheet
            :return a base mask string
            """
            samplesheet_idx_list = map(len, samplesheet_idx_list)
            samplesheet_idx_and_read_length_tuples = zip(samplesheet_idx_list, index_lengths.values())
            idx_masks = list(map(
                build_index_string,
                samplesheet_idx_and_read_length_tuples))

            if is_single_read:
                return ",".join(["y*"] + idx_masks)
            else:
                return ",".join(["y*"] + idx_masks + ["y*"])

        def by_lane(x):
            return x.lane
        sample_rows_sorted_by_lane = sorted(samplesheet.samples, key=by_lane)
        lanes_and_indexes = groupby(sample_rows_sorted_by_lane, by_lane)

        first_sample_in_each_lane = {k: next(v) for k, v in lanes_and_indexes}

        base_masks = {}
        for lane, sample_row in first_sample_in_each_lane.items():
            if sample_row.index2:
                base_masks[lane] = construct_base_mask([sample_row.index1.strip(), sample_row.index2.strip()])
            else:
                base_masks[lane] = construct_base_mask([sample_row.index1.strip(), ""])

        return base_masks


class BclConvertRunnerFactory:
    """
    Generates new bclconvert runners according to the config passed.
    Will determine the correct runner to use based on the config,
    and the it's known binaries.
    """

    def __init__(self, config):
        """
        Instantiate a new BclConvertRunnerFactory
        :param config: to use
        """
        self.config = config
        self.bclconvert_mappings = config["bclconvert"]["versions"]

    def _get_class_creator(self, version):
        """
        Based on the config provided in `bclconvert`, and the passed
        version, this will return a function that can be used to provide
        create a appropriate bclconvert runner.
        :param: version to look for mapping for
        :return: a function that can be used to create a bclconvert runner.
        """

        def _get_bclconvert_runner(self, config, binary):
            return BclConvertRunner(config, binary)

        function_name = self.bclconvert_mappings[version]["class_creation_function"]
        function = locals()[function_name]
        return function

    def _get_binary(self, version):
        """
        Get the binary for the bclconvert version we are using.
        """
        return self.bclconvert_mappings[version]["binary"]

    def create_bclconvert_runner(self, config):
        """
        Uses higher order functions to create a correct runner based
        on the config passed to it.
        """
        version = config.bclconvert_version
        if version in self.bclconvert_mappings:
            clazz = self._get_class_creator(version)
            binary = self._get_binary(version)
            return clazz(self, config, binary)
        else:
            raise LookupError(f"Couldn't find a valid config mapping for bclconvert version {version}.")


class BaseBclConvertRunner(object):
    """
    Base class for bclconvert runners. Provides common functionality for running commands, etc.
    """
    def __init__(self, config, binary):
        self.config = config
        self.binary = binary
        self.command = None

    def version(self):
        """
        Get the version of bclconvert run. Preferably defer the
        decision of which version it was to the binary (instead of
        trusting that the configured versions are correct).
        :return: the bclconvert version used.
        """
        raise NotImplementedError("Subclasses should implement this!")

    def construct_command(self):
        """
        Implement this in subclass
        :return: a command to be run by `run`, or other external command runner.
        """
        raise NotImplementedError("Subclasses should implement this!")

    def validate_output(self):

        def _parent_dir(d):
            return os.path.abspath(os.path.join(d, os.path.pardir))

        abs_path_of_allowed_dirs = map(os.path.abspath, self.config.general_config['allowed_output_folders'])
        is_located_in_parent_dir = _parent_dir(self.config.output) in abs_path_of_allowed_dirs

        if not is_located_in_parent_dir:
            error_string = f"Invalid output directory {self.config.output} was specified." \
                           f" Allowed dirs were: {self.config.general_config['allowed_output_folders']}"
            log.error(error_string)
            raise ArteriaUsageException(error_string)

    def delete_output(self):
        """
        Delete the output directory if it exists and  the output path is valid
        :return: None
        """
        self.validate_output()
        log.info(f"Found a directory at output path {self.config.output}, will remove it.")
        try:
            shutil.rmtree(self.config.output)
        except OSError as e:
            # Ignore if the error is of type "No such file or directory"
            if e.errno == errno.ENOENT:
                log.debug(f"No such output directory, with path: {self.config.output} will not remove it.")
                pass
            else:
                log.error(f"Got error with error number {e.errno} when trying to remove dir: {self.config.output}")
                raise e

    def symlink_output_to_unaligned(self):
        """
        Create a symlink from `runfolder/Unaligned` to what has been defined as the output directory.
        :raises: OSError if there was any problem creating the symlink, except for that it was already
                         there, in which case, do nothing.
        """
        link_path = self.config.runfolder_input + "/Unaligned"
        link_target_path = self.config.output

        try:
            log.debug(f"Create symlink from {link_path} to {link_target_path}.")
            os.symlink(link_target_path, link_path, target_is_directory=True)
        except OSError as e:
            if e.errno == errno.EEXIST:
                log.warning(f"Symlink from {link_path} to {link_target_path} already exits, will remove it and recreate it...")
                log.warning(f"Removing link: {link_path}")
                os.remove(link_path)
                os.symlink(link_target_path, link_path)
            else:
                log.error(f"Problem creating symlink from {link_path} to {link_target_path}. Message: {e.message}")
                raise e


class BclConvertRunner(BaseBclConvertRunner):
    """
    Runs bclconvert
    """

    def __init__(self, config, binary):
        BaseBclConvertRunner.__init__(self, config, binary)

    def version(self):
        """
        Since there is no way of extracting the version used in bclconvert 1.x we
        will have to trust the the configured version is correct.
        :return: version of bclconvert used as specified by config.
        """
        return self.config.bclconvert_version

    def construct_command(self):

        ##################################
        # First run configurebclconvert.pl
        ##################################

        # Assumes configureBclToFastq.pl on path
        commandline_collection = [
            self.binary,
            "--bcl-inputdirectory", self.config.runfolder_input,
            "--sample-sheet", self.config.samplesheet_file,
            "--output-directory", self.config.output,
            "--force"  # overwrite output if it exists.
        ]

        samplesheet = Samplesheet(self.config.samplesheet_file)

        if self.config.barcode_mismatches:
            commandline_collection.extend(["--mismatches", self.config.barcode_mismatches])

        if self.config.tiles:
            commandline_collection.extend(["--tiles", self.config.tiles])

        if self.config.exclude_tiles:
            commandline_collection.extend(["--exclude-tiles", self.config.exclude_tiles])

        if self.config.bcl_sampleproject_subdirectories:
            commandline_collection.extend(["--bcl-sampleproject-subdirectories", f"{self.config.bcl_sampleproject_subdirectories}"])

        if self.config.sample_name_column_enabled:
            commandline_collection.extend(["--sample-name-column-enabled", f"{self.config.sample_name_column_enabled}"])

        if self.config.strict_mode:
            commandline_collection.extend(["--strict-mode", "true"])
        else:
            commandline_collection.extend(["--strict-mode", "false"])

        if self.config.fastq_gzip_compression_level:
            commandline_collection.extend(["--fastq-gzip-compression-level", f"{self.config.fastq_gzip_compression_level}"])

        if self.config.no_lane_splitting:
            commandline_collection.extend(["--no-lane-splitting", "true"])
        else:
            commandline_collection.extend(["--no-lane-splitting", "false"])

        commandline_collection.extend(["--bcl-num-parallel-tiles", f"{self.config.bcl_num_parallel_tiles}"])

        commandline_collection.extend(["--bcl-num-conversion-threads", f"{self.config.bcl_num_conversion_threads}"])
        commandline_collection.extend(["--bcl-num-compression-threads", f"{self.config.bcl_num_compression_threads}"])
        commandline_collection.extend(["--bcl-num-decompression-threads", f"{self.config.bcl_num_decompression_threads}"])

        if self.config.additional_args:
            commandline_collection.extend(self.config.additional_args)

        log.debug("command: " + str(commandline_collection))
        return commandline_collection
