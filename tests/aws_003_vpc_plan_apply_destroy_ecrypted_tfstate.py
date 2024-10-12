#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, hcl, tempfile, json
import unittest
import cloudicorn
from cloudicorn.core import Project, TfStateStoreAwsS3
from cloudicorn.core import assert_aws_creds, get_random_string
import random
import string

import boto3
from botocore.exceptions import ClientError
import botocore

TEST_S3_BUCKET = os.getenv("TEST_S3_BUCKET", None)

class TestAwsPlanVpcEncrypted(unittest.TestCase):

    def setUp(self):
        # make copy of env vars
        self.env_orig = os.environ.copy()

        self.boto_client = boto3.client('ec2')
        assert TEST_S3_BUCKET != None

        self.run_string = get_random_string(10)
        assert_aws_creds()

    def tearDown(self):
        # reset environment vars to beginning of run
        # to avoid spillover into other unit tests
        os.environ = self.env_orig

        response = self.describe_vpcs()
        
        for r in response['Vpcs']:
            VpcId = r['VpcId']

            response = self.boto_client.delete_vpc(
                VpcId=VpcId,
            )        

    def describe_vpcs(self):
        return self.boto_client.describe_vpcs(Filters=[{'Name':'tag:Name','Values':["example vpc {}".format(self.run_string)]}])
    
    def test_apply_delete_encrypted_tfstate(self):
        d = tempfile.mkdtemp()
        tfstate_file = "{}/terraform.tfstate".format(d)

        cdir = "aws/vpc_tfstate"

        random_passphrase = get_random_string(32)

        os.environ["CLOUDICORN_TFSTATE_STORE_ENCRYPTION_PASSPHRASE"] = random_passphrase
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

        assert crs.is_encrypted

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
