# -*- coding: utf-8 -*-
import logging
import pathlib
import unittest
from unittest.mock import patch
from installed_clients.DataFileUtilClient import DataFileUtil
import os
import subprocess
import time
import unittest

from configparser import ConfigParser
from shutil import copyfile

from kb_bedtools.kb_bedtoolsImpl import kb_bedtools
from kb_bedtools.kb_bedtoolsServer import MethodContext
from kb_bedtools.authclient import KBaseAuth as _KBaseAuth
from kb_bedtools.utils import BamConversion

from installed_clients.WorkspaceClient import Workspace

def mock_download_staging_file(params):
    print("Mocking download_staging_file with:", params)
    staging_file_name = os.path.basename(params["staging_file_subdir_path"])

    source_path = os.path.join("/home/ac.ballen/kb_bedtools/test", staging_file_name)
    dest_path = os.path.join("/kb/module/work/tmp", staging_file_name)

    shutil.copy(source_path, dest_path)
    return {"copy_file_path": dest_path}

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

    def copy_bam_to_scratch(self):
        import shutil
        import os

        bam_src = os.path.join(os.path.dirname(__file__), "wgEncodeUwRepliSeqBg02esG1bAlnRep1.bam")
        bam_dst = os.path.join(self.scratch, "wgEncodeUwRepliSeqBg02esG1bAlnRep1.bam")

        shutil.copy(bam_src, bam_dst)
        print(f"Copied BAM file to scratch: {bam_dst}")
        return bam_dst


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

        @patch.object(DataFileUtil, "download_staging_file", side_effect=mock_download_staging_file)
        def test_your_method(self, mock_download):
                # Now when run_kb_bedtools calls download_staging_file, it uses your mock

            params = {
                "workspace_name": self.wsName,
                "reads_ref": "70257/2/1",
                "output_name": "ReadsOutputName",
                "bam_file": "wgEncodeUwRepliSeqBg02esG1bAlnRep1.bam",
                "fastq_path_name": "../../module/test/filename_end2.fq",
            }

            ret = self.serviceImpl.run_kb_bedtools(self.ctx, params)

            self.assertIn("report_name", ret[0])
            self.assertIn("report_ref", ret[0])
