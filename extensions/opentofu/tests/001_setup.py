#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import unittest
import cloudicorn
from cloudicorn.tfwrapper import Utils
from cloudicorn_opentofu import OpentofuUtils

class TestSetup(unittest.TestCase):

    def test_setup_current(self):

        retcode = cloudicorn.main(["cloudicorn", "--check-setup", "--tf-bin-path", os.path.dirname(os.path.realpath(__file__))+'/mock/mock_opentofu_current'])
        assert retcode == 0

    def test_get_version(self):
        u = OpentofuUtils(
            tf_path = os.path.dirname(os.path.realpath(__file__))+'/bin/mock_opentofu_current'
        )
        
        v, url = u.tf_currentversion()

        assert url.startswith("https://github.com/opentofu/opentofu/releases/download/")
        assert url.endswith(".zip")

        a = v.split(".")

        assert v.startswith("v")
        assert len(a) == 3

    # def test_check_setup_missing(self):
    #     u = Utils(
    #         tf_path = os.path.dirname(os.path.realpath(__file__))+'/bin/none'
    #     )

    #     missing, outdated = u.check_setup(verbose=True)

    #     assert not outdated
    #     assert  missing

if __name__ == '__main__':
    unittest.main()
