# This file has been modified from the https://github.com/arteria-project/arteria-bcl2fastq repo
# bcl2fastq/handlers/bcl2fastq_handlers.py
import json
import logging
import os

from bclconvert.lib.jobrunner import LocalQAdapter
from bclconvert.lib.bclconvert_utils import BclConvertRunnerFactory, BclConvertConfig
from bclconvert import __version__ as version
from bclconvert.lib.bclconvert_logs import BclConvertLogFileProvider
from arteria.exceptions import ArteriaUsageException
from arteria.web.state import State
from arteria.web.handlers import BaseRestHandler

log = logging.getLogger(__name__)


class BclConvertServiceMixin:
    """
    Provides bclconvert related services that can be mixed in.
    It will create adaptors to the runner service the first time a
    request is made and then keep that adaptor. These adaptors are static,
    so that only one such adaptor is created for the entire application.
    """
    _runner_service = None

    @staticmethod
    def runner_service():
        """
        Create an adaptor to the runner service unless one already exists
        """
        if BclConvertServiceMixin._runner_service:
            return BclConvertServiceMixin._runner_service
        else:
            import multiprocessing
            nbr_of_cores = multiprocessing.cpu_count()
            # TODO Make configurable
            BclConvertServiceMixin._runner_service = LocalQAdapter(nbr_of_cores=nbr_of_cores, interval=2)
            return BclConvertServiceMixin._runner_service

    _bclconvert_cmd_generation_service = None

    @staticmethod
    def bclconvert_cmd_generation_service(config):
        """
        Create a command generation service unless one already exists.
        """
        if BclConvertServiceMixin._bclconvert_cmd_generation_service:
            return BclConvertServiceMixin._bclconvert_cmd_generation_service
        else:
            BclConvertServiceMixin._bclconvert_cmd_generation_service = BclConvertRunnerFactory(config)
            return BclConvertServiceMixin._bclconvert_cmd_generation_service


class BaseBclConvertHandler(BaseRestHandler):
    """
    Base handler for bclconvert.
    """
    def initialize(self, config):
        """
        Ensures that any parameters feed to this are available
        to subclasses.
        """
        self.config = config
        self.bclconvert_log_file_provider = BclConvertLogFileProvider(self.config)


class VersionsHandler(BaseBclConvertHandler):
    """
    Get the available bclconvert versions that the
    service knows about.
    """

    def get(self):
        """
        Returns all available bclconvert versions (as defined by config).
        """
        available_versions = self.config["bclconvert"]["versions"]
        self.write_object(available_versions)


class StartHandler(BaseBclConvertHandler, BclConvertServiceMixin):
    """
    Start bclconvert
    """

    def create_config_from_request(self, runfolder, request_body):
        """
        For the specified runfolder, will look it up from the place setup in the
        configuration, and then parse additional data from the request_data object.
        This can be used to override any default setting in the resulting bclconvertConfig
        instance.
        :param runfolder: name of the runfolder we want to create a config for
        :param request_body: the body of the request. Can be empty, in which case if will not be loaded.
        :return: an instances of bclconvertConfig
        """

        if request_body:
            request_data = json.loads(request_body)
        else:
            request_data = {}

        # TODO Make sure to escape them for sec. reasons.
        bclconvert_version = ""
        runfolder_input = ""
        samplesheet = ""
        output = ""
        barcode_mismatches = ""
        tiles = ""
        exclude_tiles = ""
        use_base_mask = ""
        bcl_only_lane = None
        create_indexes = False
        bcl_num_parallel_tiles = None
        bcl_num_conversion_threads = None
        bcl_num_compression_threads = None
        bcl_num_decompression_threads = None
        additional_args = ""

        for runfolders_path in self.config["runfolder_path"]:
            if os.path.isdir(os.path.join(runfolders_path, runfolder_input)):
                runfolder_input = os.path.join(runfolders_path, runfolder)
                break

        if not os.path.isdir(runfolder_input):
            raise ArteriaUsageException(f"No such file: {runfolder_input}")

        if "bclconvert_version" in request_data:
            bclconvert_version = request_data["bclconvert_version"]

        if "output" in request_data:
            output = request_data["output"]

        if "samplesheet" in request_data:
            samplesheet = request_data["samplesheet"]

        if "barcode_mismatches" in request_data:
            barcode_mismatches = request_data["barcode_mismatches"]

        if "tiles" in request_data:
            tiles = request_data["tiles"]

        if "exclude_tiles" in request_data:
            exclude_tiles = request_data["exclude_tiles"]

        if "use_base_mask" in request_data:
            use_base_mask = request_data["use_base_mask"]

        if "create_indexes" in request_data:
            if request_data["create_indexes"] == "True":
                create_indexes = True

        if "bcl_only_lane" in request_data:
            bcl_only_lane = request_data['bcl_only_lane']

        if "bcl_num_parallel_tiles" in request_data:
            bcl_num_parallel_tiles = request_data['bcl_num_parallel_tiles']

        if "bcl_num_conversion_threads" in request_data:
            bcl_num_conversion_threads = request_data["bcl_num_conversion_threads"]

        if "bcl_num_compression_threads" in request_data:
            bcl_num_compression_threads = request_data["bcl_num_compression_threads"]

        if "bcl_num_decompression_threads" in request_data:
            bcl_num_decompression_threads = request_data["bcl_num_decompression_threads"]

        if "additional_args" in request_data:
            additional_args = request_data["additional_args"]

        config = BclConvertConfig(
            general_config=self.config,
            bclconvert_version=bclconvert_version,
            runfolder_input=runfolder_input,
            output=output,
            samplesheet=samplesheet,
            barcode_mismatches=barcode_mismatches,
            tiles=tiles,
            exclude_tiles=exclude_tiles,
            use_base_mask=use_base_mask,
            create_indexes=create_indexes,
            bcl_num_parallel_tiles=bcl_num_parallel_tiles,
            bcl_num_conversion_threads=bcl_num_conversion_threads,
            bcl_num_compression_threads=bcl_num_compression_threads,
            bcl_num_decompression_threads=bcl_num_decompression_threads,
            additional_args=additional_args)

        return config

    def post(self, runfolder):
        """
        Starts a bclconvert for a runfolder. The input data can contain extra
        parameters for bclconvert. It should be a json encoded object and
        can contain one or more of the following parameters:
         - bclconvert_version
         - output
         - samplesheet (provide the entire samplesheet in the request)
         - barcode_mismatches
         - tiles
         - use_base_mask
         - additional_args
        If these are not set defaults setup in bclconvertConfig will be
        used (and those should be good enough for most cases).

        :param runfolder: name of the runfolder we want to start bclconvert for
        """

        try:
            runfolder_config = self.create_config_from_request(runfolder, self.request.body)

            job_runner = self.bclconvert_cmd_generation_service(self.config). \
                create_bclconvert_runner(runfolder_config)
            bclconvert_version = job_runner.version()
            cmd = job_runner.construct_command()
            # If the output directory exists, we always want to clear it.
            job_runner.delete_output()
            # job_runner.symlink_output_to_unaligned()

            log_file = self.bclconvert_log_file_provider.log_file_path(runfolder)

            job_id = self.runner_service().start(
                cmd,
                nbr_of_cores=runfolder_config.nbr_of_cores,
                run_dir=runfolder_config.runfolder_input,
                stdout=log_file,
                stderr=log_file)

            log.info(
                f"Cmd: {cmd} started in {runfolder_config.runfolder_input} "
                f"with {runfolder_config.nbr_of_cores} cores. Writing logs to: {log_file}")

            reverse_url = self.reverse_url("status", job_id)
            status_end_point = f"{self.request.protocol}://{self.request.host}{reverse_url}"

            response_data = {
                "job_id": job_id,
                "bclconvert_version": bclconvert_version,
                "service_version": version,
                "link": status_end_point,
                "state": State.STARTED}

            self.set_status(202, reason="started processing")
            self.write_json(response_data)
        except ArteriaUsageException as e:
            log.warning(f"Failed starting {runfolder}. Message: {e}")
            self.send_error(status_code=500, reason=e)


class StatusHandler(BaseBclConvertHandler, BclConvertServiceMixin):
    """
    Get the status of one or all jobs.
    """
    def get(self, job_id):
        """
        Get the status of the specified job_id, or if now id is given, the
        status of all jobs.
        :param job_id: to check status for (set to empty to get status for all)
        """

        if job_id:
            status = {"state": self.runner_service().status(job_id)}
        else:
            all_status = self.runner_service().status_all()
            status_dict = {}
            for k, v in all_status.items():
                status_dict[k] = {"state": v}
            status = status_dict

        self.write_json(status)


class StopHandler(BaseBclConvertHandler, BclConvertServiceMixin):
    """
    Stop one or all jobs.
    """

    def post(self, job_id):
        """
        Stops the job with the specified id.
        :param job_id: of job to stop, or set to "all" to stop all jobs
        """
        try:
            if job_id == "all":
                log.info("Attempting to stop all jobs.")
                self.runner_service().stop_all()
                log.info("Stopped all jobs!")
                self.set_status(200)
            elif job_id:
                log.info(f"Attempting to stop job: {job_id}")
                self.runner_service().stop(job_id)
                self.set_status(200)
            else:
                ArteriaUsageException("Unknown job to stop")
        except ArteriaUsageException as e:
            log.warning(f"Failed stopping job: {job_id}. Message: {e}")
            self.send_error(500, reason=str(e))


class BclConvertLogHandler(BaseBclConvertHandler):
    """
    Gets the content of the log for a particular runfolder
    """

    def get(self, runfolder):
        """
        Get the content of the log for a particular runfolder
        :param runfolder:
        :return:
        """
        try:
            log_content = self.bclconvert_log_file_provider.get_log_for_runfolder(runfolder)
            response_data = {"runfolder": runfolder, "log": log_content}
            self.set_status(200)
            self.write_json(response_data)
        except IOError as e:
            log.warning(f"Problem with accessing {runfolder}, message: {e}")
            self.send_error(500, reason=str(e))
