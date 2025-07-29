import json
import io
import logging
import os
import subprocess
import uuid
import shutil

from collections import Counter
from shutil import copyfile

import subprocess

from Bio import SeqIO

from base import Core

MODULE_DIR = "/kb/module"
TEMPLATES_DIR = os.path.join(MODULE_DIR, "lib/templates")


class BamConversion(Core):
    def __init__(self, ctx, config, app_config, clients_class=None):
        """
        This is required to instantiate the Core App class with its defaults
        and allows you to pass in more clients as needed.
        """
        super().__init__(ctx, config, clients_class)
        self.dfu = self.clients.DataFileUtil
        self.report = self.clients.KBaseReport
        self.ru = self.clients.ReadsUtils
        self.app_config = app_config

    def do_analysis(self, params: dict):
        """
        This method is where the main computation will occur.
        """
        print(f"{json.dumps(params)=}")
        bam_file = params['bam_file']
        if os.path.isfile(bam_file):
            staging_path = bam_file
        else:
            staging_path = os.path.join("/staging/", bam_file)
        
        logging.warning(f"cwd: {os.getcwd()}")
        output_name = params['output_name']
        wsname = params['workspace_name']
        sequencing_tech = 'Illumina'
        interleaved = params['interleaved']
        if params.get('paired_end'):
            fastq_path = self.bam_to_paired_fastq(staging_path, shared_folder=self.shared_folder)
        else:
            fastq_path = self.bam_to_fastq(staging_path, shared_folder=self.shared_folder)


        reads_result = self.upload_reads(output_name, fastq_path, wsname, sequencing_tech, interleaved)


        report_info = self.report.create({
            'report': {
                'text_message': f'Successfully converted BAM to FASTQ and uploaded as Reads: {output_name}',
                'objects_created': [
                    {
                        'ref': reads_result['obj_ref'],
                        'description': 'Uploaded Reads object from FASTQ'
                    }
                ]
            },
            'workspace_name': wsname
        })

        return {
            "report_name": report_info['name'],
            "report_ref": report_info['ref']
        }

    @classmethod
    def bam_to_fastq(cls, bam_file, shared_folder=""): # add a dict parameter so those parameter could be use
        if not os.path.isfile(bam_file):
            raise FileNotFoundError(f"{bam_file} not found")

        unique_id = str(uuid.uuid4())[:8]
        temp_fastq = f"filename_end1_{unique_id}.fq"
        output_path = os.path.join(shared_folder, f"output_{unique_id}.fq")

        logging.warning(f'{">"*20}{os.getcwd()}')

        with subprocess.Popen([
            'bedtools', 'bamtofastq', '-i', bam_file, '-fq', temp_fastq
        ]) as proc:
            proc.wait()

        if not os.path.exists(temp_fastq):
            raise FileNotFoundError("bedtools did not create FASTQ file")

        if os.path.getsize(temp_fastq) < 100:
            raise ValueError("Generated FASTQ file is unexpectedly small — check input BAM or bedtools error")

        shutil.copyfile(temp_fastq, output_path)
        return output_path

    @classmethod
    def bam_to_fastq_paired(cls, bam_file, shared_folder=""):
        if not os.path.isfile(bam_file):
            raise FileNotFoundError(f"{bam_file} not found")

        unique_id = str(uuid.uuid4())[:8]
        read1_file = f"filename_end1_{unique_id}.fq"
        read2_file = f"filename_end2_{unique_id}.fq"


        logging.warning(f"{'>'*20}{os.getcwd()}")

        with subprocess.Popen([
            'bedtools', 'bamtofastq',
            '-i', bam_file,
            '-fq', read1_file,
            '-fq2', read2_file
        ]) as proc:
            proc.wait()

        if not os.path.exists(read1_file) or not os.path.exists(read2_file):
            raise FileNotFoundError("Paired-end FASTQ files were not created")

        
        output1 = os.path.join(shared_folder, f"read1_{unique_id}.fq")
        output2 = os.path.join(shared_folder, f"read2_{unique_id}.fq")
        
        shutil.copyfile(read1_file, output1)
        shutil.copyfile(read2_file, output2)

        return {"read1": output1, "read2": output2}

    def upload_reads(self, name, reads_path, workspace_name,
                     sequencing_tech=None, interleaved=None):
        """
        Upload reads back to the KBase Workspace. This method only uses the
        minimal parameters necessary to provide a demonstration. There are many
        more parameters which reads can provide, for example, interleaved, etc.
        By default, non-interleaved objects and those uploaded without a
        reverse file are saved as KBaseFile.SingleEndLibrary. See:
        https://github.com/kbaseapps/ReadsUtils/blob/master/lib/ReadsUtils/ReadsUtilsImpl.py#L115-L119
        param: filepath_to_reads - A filepath to a fastq fastq file to upload reads from
        param: wsname - The name of the workspace to upload to
        """
        ur_params = {
            "fwd_file": reads_path,
            "name": name,
            "sequencing_tech": sequencing_tech,
            "wsname": workspace_name,
            "interleaved": interleaved
            #"single_genome": single_genome
        }
        logging.warning(f">>>>>>>>>>>>>>>>>>>>{ur_params}")
        return self.ru.upload_reads(ur_params)
    
class Intersection(Core):
    def __init__(self, ctx, config, clients_class=None):
        """
        This is required to instantiate the Core App class with its defaults
        and allows you to pass in more clients as needed.
        """
        super().__init__(ctx, config, clients_class)
        self.report = self.clients.KBaseReport
        self.ru = self.clients.ReadsUtils
    
    def intersection(self, first_file, second_file):
        file1 = first_file
        file2 = second_file
        open('intersect.gff', 'w').close()
        with open('intersect.gff', 'w') as f:
            with subprocess.Popen([
                'bedtools', 'intersect', '-a', file1, '-b', file2], stdout=f) as proc:
                    proc.wait()
        out_path = os.path.join(self.shared_folder, 'intersect.gff')
        copyfile('intersect.gff', out_path)
        return out_path

    def do_analysis(self, params: dict):
        """
        This method is where the main computation will occur.
        """
        first_file = params.get('first_file')
        if not first_file:
            raise ValueError("Missing required parameter: first_file")
        second_file = params['second_file']
        output_name = params['output_name']
        wsname = params['workspace_name']
        sequencing_tech = 'Illumina'
        fastq_path = self.intersection(first_file, second_file)
        self.upload_reads(output_name, fastq_path, wsname, sequencing_tech)
        return {}

    def upload_reads(self, name, reads_path, workspace_name, sequencing_tech):
        """
        Upload reads back to the KBase Workspace. This method only uses the
        minimal parameters necessary to provide a demonstration. There are many
        more parameters which reads can provide, for example, interleaved, etc.
        By default, non-interleaved objects and those uploaded without a
        reverse file are saved as KBaseFile.SingleEndLibrary. See:
        https://github.com/kbaseapps/ReadsUtils/blob/master/lib/ReadsUtils/ReadsUtilsImpl.py#L115-L119
        param: filepath_to_reads - A filepath to a fastq fastq file to upload reads from
        param: wsname - The name of the workspace to upload to
        """
        ur_params = {
            "fwd_file": reads_path,
            "name": name,
            "wsname": workspace_name,
            "sequencing_tech" : 'Illumina'
        }
        # It is often useful to log parameters as they are passed.
        logging.warning(f">>>>>>>>>>>>>>>>>>>>{ur_params}")
