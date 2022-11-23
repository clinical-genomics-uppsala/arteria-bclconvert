# This file has been modified from the https://github.com/arteria-project/arteria-bcl2fastq repo
# bcl2fastq/lib/bcl2fastq_logs.py

class BclConvertLogFileProvider:

    def __init__(self, config):
        self.config = config

    def log_file_path(self, runfolder):
        log_base_path = self.config["bclconvert_logs_path"]
        log_file = f"{log_base_path}/{runfolder}.log"
        return log_file

    def get_log_for_runfolder(self, runfolder):
        log_path = self.log_file_path(runfolder)
        with open(log_path) as f:
            file_content = f.read()
        return file_content
