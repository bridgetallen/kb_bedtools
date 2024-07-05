# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser
import subprocess

from kb_bedtools.kb_bedtoolsImpl import kb_bedtools
from kb_bedtools.kb_bedtoolsServer import MethodContext
from kb_bedtools.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace


class kb_bedtoolsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        token = os.environ.get("KB_AUTH_TOKEN", None)
        config_file = os.environ.get("KB_DEPLOYMENT_CONFIG", None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items("kb_bedtools"):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg["auth-service-url"]
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update(
            {
                "token": token,
                "user_id": user_id,
                "provenance": [
                    {
                        "service": "kb_bedtools",
                        "method": "please_never_use_it_in_production",
                        "method_params": [],
                    }
                ],
                "authenticated": 1,
            }
        )
        cls.wsURL = cls.cfg["workspace-url"]
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = kb_bedtools(cls.cfg)
        cls.scratch = cls.cfg["scratch"]
        cls.callback_url = os.environ["SDK_CALLBACK_URL"]
        suffix = int(time.time() * 1000)
        cls.wsName = "test_ContigFilter_" + str(suffix)
        ret = cls.wsClient.create_workspace({"workspace": cls.wsName})  # noqa

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "wsName"):
            cls.wsClient.delete_workspace({"workspace": cls.wsName})
            print("Test workspace was deleted")

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    # @unittest.skip("Skip test for debugging")
    def test_your_method(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
        #ret = self.serviceImpl.run_kb_bedtools(
        #    self.ctx,
        #    {
        #        "workspace_name": self.wsName,
        #        "reads_ref": "70257/2/1",
        #        "output_name": "ReadsOutputName",
        #    },
        #)
        with self.assertRaises(KeyError):
            self.serviceImpl.run_kb_bedtools(self.ctx, {'workspace_name': self.wsName})
        # next steps:
        # - download report
        # - assert that the report has expected contents
    
    def test_bam_to_fastq(self):
        bam_filename = 'wgEncodeUwRepliSeqBg02esG1bAlnRep1.bam'
        with open(bam_filename, 'rb') as file:
            bam_data = file.read().decode('utf-8', 'ignore')
        print(bam_data)

        open('filename_end1.fq', 'w').close()
        open('filename_end2.fq', 'w').close()

        with open('filename_end2.fq', 'w') as f:
            result = subprocess.Popen(['bedtools', 'bamtofastq', '-i', bam_filename, '-fq', 
                                       'filename_end1.fq', '-fq2', '/dev/stdout'], stdout=f)
            result.wait()

        with open('filename_end2.fq', 'r') as fq_together:
            print(fq_together.read())
        if result.returncode == 0:
            print("Command executed successfully")
        else:
            print(f"Error occurred while executing command ")
