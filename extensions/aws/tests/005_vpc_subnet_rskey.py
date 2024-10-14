#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import unittest
import cloudicorn
from cloudicorn.core import ComponentException
from cloudicorn_aws import assert_aws_creds
import random
import string

import boto3

TEST_S3_BUCKET = os.getenv("TEST_S3_BUCKET", None)

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return str(result_str)

class TestAwsVpcSubnet(unittest.TestCase):

    def setUp(self):
        # make copy of env vars
        
        self.boto_client = boto3.client('ec2')
        assert TEST_S3_BUCKET != None

        self.run_string = get_random_string(10)

        assert_aws_creds()

        # make vpc
        cdir = "components/vpc_tfstate"

        retcode = cloudicorn.main(["cloudicorn", "apply", cdir, '--force', '--set-var', 'run_id={}'.format(self.run_string)])
        assert retcode == 0

    def tearDown(self):
        cdir = "components/subnet_tfstate"

        retcode = cloudicorn.main(["cloudicorn", "destroy", cdir, '--force', '--set-var', 'run_id={}'.format(self.run_string)])
        assert retcode == 0

        response = self.describe_subnets()

        for r in response['Subnets']:
            SubnetId = r['SubnetId']

            response = self.boto_client.delete_subnet(
                SubnetId=SubnetId,
            )        

        response = self.describe_vpcs()
       
        for r in response['Vpcs']:
            VpcId = r['VpcId']

            response = self.boto_client.delete_vpc(
                VpcId=VpcId,
            )        

    def describe_vpcs(self):
        return self.boto_client.describe_vpcs(Filters=[{'Name':'tag:Name','Values':["example vpc {}".format(self.run_string)]}])
    
    def describe_subnets(self):
        return self.boto_client.describe_subnets(Filters=[{'Name':'tag:Name','Values':["example subnet {}".format(self.run_string)]}])
    
    def test_apply_subnet_success(self):
        cdir = "components/subnet_tfstate"
        retcode = cloudicorn.main(["cloudicorn", "apply", cdir, '--force', '--set-var', 'run_id={}'.format(self.run_string)])
        assert retcode == 0

        # second apply, should also succeed with no changes
        retcode = cloudicorn.main(["cloudicorn", "apply", cdir, '--force', '--set-var', 'run_id={}'.format(self.run_string)])
        assert retcode == 0

    def test_apply_delete_subnet_failmode_not_a_component(self):
        cdir = "components/subnet_tfstate_fail"
        try:
            cloudicorn.main(["cloudicorn", "apply", cdir, '--force',
                    '--set-var', 'run_id={}'.format(self.run_string),
                    '--set-var', 'tfstate_link=FAIL'
                    ])
            assert False
        except ComponentException as e:
            assert "must point to a component" in str(e)

    def test_apply_delete_subnet_failmode_no_such_tfstate_output(self):
        cdir = "components/subnet_tfstate_fail"
        try:
            cloudicorn.main(["cloudicorn", "apply", cdir, '--force',
                    '--set-var', 'run_id={}'.format(self.run_string),
                    '--set-var', 'tfstate_link=components/vpc_tfstate:lol'
                    ])
            assert False
        except ComponentException as e:
            assert "No such output in component" in str(e)




if __name__ == '__main__':
    unittest.main()
