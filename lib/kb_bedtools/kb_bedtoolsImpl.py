# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import subprocess

from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.ReadsUtilsClient import ReadsUtils
from base import Core

from kb_bedtools.utils import BamConversion, Intersection

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
        version = subprocess.check_output(["bedtools", "--version"])
        print("BEDTOOLS VERSION IN CONTAINER:", version.decode())

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
        output = bam.do_analysis(params)

        output = bam.do_analysis(params)

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_kb_bedtools return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
        #END run_kb_bedtools
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
