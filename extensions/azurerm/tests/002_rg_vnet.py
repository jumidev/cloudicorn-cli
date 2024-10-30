#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import unittest
from cloudicorn.core import get_random_string
from cloudicorn.tfwrapper import TFException

from cloudicorn_azurerm import assert_azurerm_sp_creds, AzureUtils
import datetime, cloudicorn

TEST_AZURE_STORAGE_ACCOUNT = os.getenv("TEST_AZURE_STORAGE_ACCOUNT", None)
TEST_AZURE_STORAGE_CONTAINER = os.getenv("TEST_AZURE_STORAGE_CONTAINER", None)

class TestAzureRgVnetStateStore(unittest.TestCase):

    def setUp(self):
        self.project_args=["--project-dir", "components"]

        assert_azurerm_sp_creds()
        assert TEST_AZURE_STORAGE_ACCOUNT != None
        assert TEST_AZURE_STORAGE_CONTAINER != None
        self.current_date_slug = datetime.date.today().strftime('%Y-%m-%d')
        self.run_string = get_random_string(10)
        self.run_string2 = get_random_string(10)
        self.azure_utils = AzureUtils()
        self.resource_client =  self.azure_utils.resource_client
        cdir = "resource_group_vnet"

        retcode = cloudicorn.main(["cloudicorn", "apply", cdir, '--force', '--set-var', "run_id={}".format(self.run_string), *self.project_args])
        assert retcode == 0

        retcode = cloudicorn.main(["cloudicorn", "apply", cdir, '--force', '--set-var', "run_id={}".format(self.run_string2), *self.project_args])
        assert retcode == 0

    def tearDown(self):
        print("cleaning up resource groups...")
        self.resource_client.resource_groups.begin_delete("test_{}".format(self.run_string))
        self.resource_client.resource_groups.begin_delete("test_{}".format(self.run_string2))

    def test_vnet_asg_etc_success(self):
        cdirs = [
            "virtual_network",
            "asg",
            "nsg",
            "subnet"
        ]
        for cdir in cdirs: 

            retcode = cloudicorn.main(["cloudicorn", "apply", cdir, '--force', '--set-var', "run_id={}".format(self.run_string), *self.project_args])
            assert retcode == 0

    def test_vnet_asg_etc_fail_then_success(self):

        cdir = "nsg_failapply"
        try:
            retcode = cloudicorn.main(["cloudicorn", "apply", cdir, '--force', '--set-var', 'fail_rule_priority=300', '--set-var', "run_id={}".format(self.run_string2), *self.project_args])
            assert False
        except TFException:
            pass
    
        retcode = cloudicorn.main(["cloudicorn", "apply", cdir, '--force', '--set-var', 'fail_rule_priority=301', '--set-var', "run_id={}".format(self.run_string2), *self.project_args])
        assert retcode == 0

if __name__ == '__main__':
    unittest.main()
