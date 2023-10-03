#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, shutil
import unittest
from tbcore import assert_azurerm_sp_creds, get_random_string, AzureUtils
import hcl, tempfile, datetime, tb
from pathlib import Path


from azure.identity import EnvironmentCredential

TEST_AZURE_STORAGE_ACCOUNT = os.getenv("TEST_AZURE_STORAGE_ACCOUNT", None)
TEST_AZURE_STORAGE_CONTAINER = os.getenv("TEST_AZURE_STORAGE_CONTAINER", None)

class TestTbAzureRgStateStore(unittest.TestCase):

    def setUp(self):
        assert_azurerm_sp_creds()
        assert TEST_AZURE_STORAGE_ACCOUNT != None
        assert TEST_AZURE_STORAGE_CONTAINER != None
        self.current_date_slug = datetime.date.today().strftime('%Y-%m-%d')
        self.run_string = get_random_string(10)
        self.azure_utils = AzureUtils()
        self.resource_client =  self.azure_utils.resource_client
        
    def tearDown(self):
        self.resource_client.resource_groups.begin_delete("test_{}".format(self.run_string))

    def test_rg(self):

        cdir = "azurerm/resource_group"

        retcode = tb.main(["tb", "apply", cdir, '--force', '--set-var', "run_id={}".format(self.run_string)])
        assert retcode == 0

        # second apply, should not change anything
        retcode = tb.main(["tb", "apply", cdir, '--force', '--set-var', "run_id={}".format(self.run_string)])
        assert retcode == 0

if __name__ == '__main__':
    unittest.main()
