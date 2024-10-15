#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import unittest
import cloudicorn
from cloudicorn.tfwrapper import Utils

class TestSetup(unittest.TestCase):

    def test_setup_current(self):

        os.environ["TERRAFORM_BIN"] = os.path.dirname(os.path.realpath(__file__))+'/bin/mock_terraform_current'
        retcode = cloudicorn.main(["cloudicorn", "--check-setup"])
        assert retcode == 0

    def test_check_setup_outdated(self):
        u = Utils(
            tf_path = os.path.dirname(os.path.realpath(__file__))+'/bin/mock_terraform_outdated'
        )

        missing, outdated = u.check_setup(verbose=True)

        assert not missing
        assert outdated

    def test_check_setup_missing(self):
        u = Utils(
            tf_path = os.path.dirname(os.path.realpath(__file__))+'/bin/none'
        )

        missing, outdated = u.check_setup(verbose=True)

        assert not outdated
        assert  missing

if __name__ == '__main__':
    unittest.main()
