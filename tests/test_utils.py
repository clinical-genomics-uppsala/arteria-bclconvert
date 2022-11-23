# This file has been modified from the https://github.com/arteria-project/arteria-bcl2fastq repo
# bcl2fastq/tests/test_utils_logs.py

from bclconvert.lib.bclconvert_utils import BCLConvertRunner, BclConvertConfig

class TestUtils:


    DUMMY_SAMPLESHEET_STRING =  """[Header],,,,,,,,,,,
IEMFileVersion,4,,,,,,,,,,
Experiment Name,Hiseq-2500-dual-index,,,,,,,,,,
Date,8/13/2015,,,,,,,,,,
Workflow,Resequencing,,,,,,,,,,
Application,Human Genome Resequencing,,,,,,,,,,
Assay,TruSeq HT,,,,,,,,,,
Description,,,,,,,,,,,
Chemistry,Amplicon,,,,,,,,,,
,,,,,,,,,,,
[Reads],,,,,,,,,,,
151,,,,,,,,,,,
151,,,,,,,,,,,
,,,,,,,,,,,
[Settings],,,,,,,,,,,
FlagPCRDuplicates,1,,,,,,,,,,
Adapter,AGATCGGAAGAGCACACGTCTGAACTCCAGTCA,,,,,,,,,,
AdapterRead2,AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT,,,,,,,,,,
,,,,,,,,,,,
[Data],,,,,,,,,,,
Lane,Sample_ID,Sample_Name,Sample_Plate,Sample_Well,I7_Index_ID,index,I5_Index_ID,index2,Sample_Project,Description,GenomeFolder
1,1,1,,,D701,ATTACTCG,D501,TATAGCCT,Test,Hiseq2500-dual-index,Homo_sapiens\UCSC\hg19\Sequence\WholeGenomeFasta
2,2,2,,,D702,TCCGGA,D503,,Test,Hiseq2500-dual-index,Homo_sapiens\UCSC\hg19\Sequence\WholeGenomeFasta
3,3,3,,,D703,CGCTCA,D503,,Test,Hiseq2500-dual-index,Homo_sapiens\UCSC\hg19\Sequence\WholeGenomeFasta
4,4,4,,,D704,GAGATTC,D504,,Test,Hiseq2500-dual-index,Homo_sapiens\UCSC\hg19\Sequence\WholeGenomeFasta
5,5,5,,,D705,ATTCAGA,D505,,Test,Hiseq2500-dual-index,Homo_sapiens\UCSC\hg19\Sequence\WholeGenomeFasta
6,6,6,,,D706,GAATTCG,D506,,Test,Hiseq2500-dual-index,Homo_sapiens\UCSC\hg19\Sequence\WholeGenomeFasta
7,7,7,,,D707,CTGAAGC,D507,,Test,Hiseq2500-dual-index,Homo_sapiens\UCSC\hg19\Sequence\WholeGenomeFasta
8,8,8,,,D708,TAATGCG,D508,,Test,Hiseq2500-dual-index,Homo_sapiens\UCSC\hg19\Sequence\WholeGenomeFasta"""


class DummyConfig:
    DUMMY_CONFIG = { "runfolder_path": "/data/biotank3/runfolders",
                     "default_output_path": "test",
                     "bclconvert":
                         {"versions":
                              {"2.15.2":
                                   {"class_creation_function": "_get_bclconvert2x_runner",
                                    "binary": "/path/to/bclconvert"},
                               "1.8.4":
                                   {"class_creation_function": "_get_bclconvert1x_runner",
                                    "binary": "/path/to/bclconvert"}}},
                     "machine_type":
                         {"MiSeq": {"bclconvert_version": "1.8.4"},
                          "HiSeq X": {"bclconvert_version": "2.15.2"},
                          "HiSeq 2500": {"bclconvert_version": "1.8.4"},
                          "HiSeq 4000": {"bclconvert_version": "1.8.4"},
                          "HiSeq 2000": {"bclconvert_version": "1.8.4"},
                          "NextSeq 500": {"bclconvert_version": "1.8.4"}},
                     "bclconvert_logs_path": "/tmp/",
                     "allowed_output_folders": ['/foo/bar']}

    def __getitem__(self, key):
        return self.DUMMY_CONFIG[key]

class DummyRunnerConfig(BclConvertConfig):
    def __init__(self, output, general_config):
        self.output = output
        self.general_config = general_config


class FakeRunner(BCLConvertRunner):
    def __init__(self, dummy_version, config):
        self.dummy_version = dummy_version
        self.config = config

    def version(self):
        return str(self.dummy_version)

    def construct_command(self):
        return "fake_bcl_command"
