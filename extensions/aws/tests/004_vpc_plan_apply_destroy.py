#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, hcl, tempfile, json
import unittest
import cloudicorn
from cloudicorn.core import Project
from cloudicorn_aws import assert_aws_creds, TfStateStoreAwsS3
import random
import string

import boto3

TEST_S3_BUCKET = os.getenv("TEST_S3_BUCKET", None)

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return str(result_str)

class TestAwsPlanVpc(unittest.TestCase):

    def setUp(self):       
        
        self.boto_client = boto3.client('ec2')
        assert TEST_S3_BUCKET != None

        self.run_string = get_random_string(10)
        assert_aws_creds()

    def tearDown(self):

        response = self.describe_vpcs()
        
        for r in response['Vpcs']:
            VpcId = r['VpcId']

            response = self.boto_client.delete_vpc(
                VpcId=VpcId,
            )        

    def test_plan(self):
        retcode = cloudicorn.main(["cloudicorn", "plan", "components/vpc", "--allow-no-tfstate-store"])
        assert retcode == 0

    def describe_vpcs(self):
        return self.boto_client.describe_vpcs(Filters=[{'Name':'tag:Name','Values':["example vpc {}".format(self.run_string)]}])
    
    def test_apply_delete(self):
        d = tempfile.mkdtemp()
        tfstate_file = "{}/terraform.tfstate".format(d)

        cdir = "components/vpc_tfstate"

        retcode = cloudicorn.main(["cloudicorn", "apply", cdir, '--force', '--set-var', "run_id={}".format(self.run_string)])
        assert retcode == 0

        # assert vpc exists
        response = self.describe_vpcs()
        
        count = 0
        for r in response['Vpcs']:
            count += 1

        assert count == 1

        # check that remote state is present on s3
        project = Project(git_filtered=False, project_vars={'run_id': self.run_string})
        project.set_component_dir(cdir)
        project.parse_component()
        obj = hcl.loads(project.hclfile)

        crs = TfStateStoreAwsS3(args=obj["tfstate_store"], localpath=tfstate_file)

        crs.fetch()

        with open(tfstate_file, 'r') as fh:
            rs = json.load(fh)

        assert rs["outputs"]["name"]["value"] == "example vpc {}".format(self.run_string)

        # apply again, should return 0
        retcode = cloudicorn.main(["cloudicorn", "apply", cdir, '--force', '--set-var', "run_id={}".format(self.run_string)])
        assert retcode == 0

        # now destroy
        retcode = cloudicorn.main(["cloudicorn", "destroy", cdir, '--force', '--set-var', "run_id={}".format(self.run_string)])
        assert retcode == 0

        # assert vpc gone
        response = self.describe_vpcs()
        
        count = 0
        for r in response['Vpcs']:
            count += 1

        assert count == 0


if __name__ == '__main__':
    unittest.main()
