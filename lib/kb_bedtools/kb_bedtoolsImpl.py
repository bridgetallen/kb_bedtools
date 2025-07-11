# -*- coding: utf-8 -*-
#BEGIN_HEADER
import json
import logging
import os
import subprocess

from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.ReadsUtilsClient import ReadsUtils
from .utils import ExampleReadsApp, BamConversion, Intersection
from kb_bedtools.utils import preview_bam_reads
from base import Core


#END_HEADER


class kb_bedtools:
    '''
    Module Name:
    kb_bedtools

    Module Description:
    A KBase module: kb_bedtools
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "git@github.com:Peanut16/kb_bedtools.git"
    GIT_COMMIT_HASH = "91f4028271383252cb2d7622790d076720617f4c"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        self.config = config
        #END_CONSTRUCTOR
        pass


    def run_kb_bedtools(self, ctx, params):
        """
        App which takes a BAM file and returns a Fastq file
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_kb_bedtools

        config = dict(
            callback_url=self.callback_url,
            shared_folder=self.shared_folder,
            clients=dict(
                DataFileUtil=DataFileUtil,
                KBaseReport=KBaseReport,
                ReadsUtils=ReadsUtils
            ),
        )
        bam = BamConversion(ctx, config=config, app_config=self.config)
        #bam.bam_to_fastq(params['bam_file'], config['shared_folder'])
        output = bam.do_analysis(params)
        #fastq_path = bam.bam_to_fastq(params['bam_file'])        #ExampleReadsApp.upload_reads(self, params['name'], params['reads_path'], params['wsname']) 
        #era = ExampleReadsApp(ctx, config=config)
        #era.upload_reads(params["bam_file"], params["read_ref"], params["workspace_name"])
    
        #out_path = os.path.join(self.shared_folder, 'filename_end1')
        #logging.warning(f">>>>>>>>>>>>>>>>>>>>{fastq_path}")
        # bam.upload_reads(params['output_name'], fastq_path, params['workspace_name']) 

        #ExampleReadsApp.upload_reads(self, params['name'], params['reads_path'], params['wsname']) #might not need this
        # Download Reads

        #era = ExampleReadsApp(ctx, config=config)
        #output = era.do_analysis(params)

        output = {}
        #END run_kb_bedtools

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_kb_bedtools return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def run_kb_bedtools_intersect(self, ctx, params):
        """
        App which takes GFF files and do the intersection command
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_kb_bedtools_intersect
        config = dict(
            callback_url=self.callback_url,
            shared_folder=self.shared_folder,
            clients=dict(
                KBaseReport=KBaseReport,
                ReadsUtils=ReadsUtils
            ),
        )
        
        intersect = Intersection(ctx, config=config)
        output = intersect.do_analysis(params)
        #END run_kb_bedtools_intersect

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_kb_bedtools_intersect return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
