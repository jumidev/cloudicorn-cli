#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import yaml
import cloudicorn, cloudicorn.core
from cloudicorn.core import hcldump, get_random_string, Project, ProjectException
import hcl


class TestSanity(unittest.TestCase):

    def setUp(self):
        self.project_args=["--project-dir", "mock"]
        
    def tearDown(self):
        pass

    def test_bad_hclt(self):
        try:
            retcode = cloudicorn.main(["cloudicorn", "parse", "badhclt", *self.project_args])
            assert False
        except cloudicorn.core.HclParseException:
            pass

    def test_good_hclt(self):
        retcode = cloudicorn.main(["cloudicorn", "parse", "goodhclt", *self.project_args])
        assert retcode == 0

    def test_bad_yml(self):
        try:
            retcode = cloudicorn.main(["cloudicorn", "parse", "withvars/badyml", *self.project_args])
            assert False
        except yaml.scanner.ScannerError:
            pass

    def test_no_component(self):
        retcode = cloudicorn.main(["cloudicorn", "parse", "not/a/component", *self.project_args])
        assert retcode == -1

    def test_list_components(self):
        retcode = cloudicorn.main(["cloudicorn", "plan", *self.project_args])
        assert retcode == 100

    def test_missing_remote_state_block(self):
        retcode = cloudicorn.main(["cloudicorn", "plan", "goodhclt", "--key", "COMPONENT_DIRNAME", *self.project_args])
        assert retcode == 110

    def test_parse_missingvars(self):
        retcode = cloudicorn.main(["cloudicorn", "parse", "withvars/missingvars", *self.project_args])
        assert retcode == 120 # not all variables substituted
    
    def test_parse_withvars(self):
        retcode = cloudicorn.main(["cloudicorn", "parse", "withvars/withvars", *self.project_args])
        assert retcode == 0 # all variables substituted

    def test_showvars_withvars(self):
        retcode = cloudicorn.main(["cloudicorn", "showvars", "withvars/withvars", *self.project_args])
        assert retcode == 0 # all variables substituted

    def test_bundle(self):
        pdira = "mock"
        bundle1 = "withvars"
        project = Project(git_filtered=False,wdir=pdira)

        assert project.component_type(bundle1) == "bundle"
    
        retcode = cloudicorn.main(["cloudicorn", "parse", "withvars", *self.project_args])
        assert retcode == 0

    def test_bundle_dry(self):
        retcode = cloudicorn.main(["cloudicorn", "parse", "withvars", "--dry", *self.project_args])
        print(retcode)
        assert retcode == 0

    def test_hcldump(self):
        l1 = ["horses", "dogs", 'cats', "mice", "owls"]
        l2 = ["asia", "europe", "northamerica", 'africa', 'australia', "southamerica"]
        l3 = [23,24,65,98,6555]

        # simple list, should fail
        try:
            hcls = hcldump(l1)
            assert False
        except cloudicorn.core.HclDumpException:
            pass

        # dict of strs, should succeed
        o = {}
        for k in l2:
            o[k] = get_random_string(10)

        hcls = hcldump(o)

        o2 = hcl.loads(hcls)
        assert type(o2) == dict

        # dict of ints, should succeed
        o = {}
        i = 0
        for k in l1:
            o[k] = l3[i]
            i+=1

        hcls = hcldump(o)

        o2 = hcl.loads(hcls)
        assert type(o2) == dict

        # dict of list of strs, should succeed
        o = {}
        for k in l1:
            o[k] = []
            for k2 in l2:
                o[k].append(k2)

        hcls = hcldump(o)

        o2 = hcl.loads(hcls)
        assert type(o2) == dict

    def test_project_root_dir(self):
        pdira = "mock"
        bundle1 = "withvars"
        project = Project(git_filtered=False,wdir=pdira)


    def test_wrong_project_dir(self):
        try:
            retcode = cloudicorn.main(["cloudicorn", "parse", "not_a_project_dir"])
            assert False
        except ProjectException:
            assert True

    def test_find_project_root(self):
        project = Project(git_filtered=False)
        assert not project.check_project_dir()
        cdir = "mock/withvars"
        folder, component_reldir = project.find_project_root(cdir)

        # inject value back into instance
        project.wdir=folder

        assert component_reldir == "withvars"
        assert project.check_project_dir()

if __name__ == '__main__':
    unittest.main()
