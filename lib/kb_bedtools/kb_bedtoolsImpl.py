# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import subprocess

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.ReadsUtilsClient import ReadsUtils
from .utils import ExampleReadsApp
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
    GIT_URL = ""
    GIT_COMMIT_HASH = ""

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
        #END_CONSTRUCTOR
        pass

    def run_kb_bedtools(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
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
                KBaseReport=KBaseReport,
                ReadsUtils=ReadsUtils
            ),
        )

        bam_filename = params['bam_file']
        with open(bam_filename, 'rb') as file:
            bam_data = file.read().decode('utf-8', 'ignore')
        print(bam_data)
        open('filename_end1.fq', 'w').close()
        open('filename_end2.fq', 'w').close()
        with open('filename_end2.fq', 'w') as f:
            result = subprocess.Popen(['bedtools', 'bamtofastq', '-i', bam_filename, '-fq', 
                                       'filename_end1.fq', '-fq2', '/dev/stdout'], stdout=f)
        # Download Reads

        era = ExampleReadsApp(ctx, config=config)
        output = era.do_analysis(params)

        #END run_kb_bedtools

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_kb_bedtools return value ' +
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
