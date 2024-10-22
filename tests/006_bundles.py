#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, shutil
import unittest
import cloudicorn, tempfile, json
from cloudicorn.core import Project


class TestBundles(unittest.TestCase):

    def setUp(self):
        self.root_dir = tempfile.mkdtemp()
        #shutil.copytree("mock/mockprojects", self.root_dir, dirs_exist_ok=True)
        #self.d_orig = os.getcwd()
        #os.chdir(self.root_dir)

    def tearDown(self):
        shutil.rmtree(self.root_dir)


    def test_mock_project_bundle_ordering(self):
        pdira = "mock/mockbundles/a"
        bundle1 = "dir1"
        bundle2 = "dir2"
        project = Project(git_filtered=False,wdir=pdira)

        assert project.component_type(bundle1) == "bundle"

        components = project.get_bundle(bundle1)

        ordered = []

        for c in components:
            ordered.append(c)

        s = sorted(ordered)
        assert s == ordered

        # bundle2 with explicit reverse ordering
        assert project.component_type(bundle2) == "bundle"

        components = project.get_bundle(bundle2)

        ordered = []

        for c in components:
            ordered.append(c)

        s = sorted(ordered, reverse=True)
        assert s == ordered


    def test_mock_project_bundle_list_apply(self):

        pdira = "mock/mockbundles/a"
        bundle = "dir1"
        p = tempfile.mkdtemp()

        retcode = cloudicorn.main(["cloudicorn", "apply", "{}/{}".format(pdira, bundle), "--force", 
                           "--set-var", "tfstate_store_path_a={}".format(p)])
        
        assert retcode == 0 # all variables substituted

        with open("{}/terraform.tfstate".format(p), "r") as fh:
            obj = json.load(fh)

if __name__ == '__main__':
    unittest.main()
