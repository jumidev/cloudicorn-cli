#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from datetime import datetime, timedelta

from cloudicorn.core import TfStateStore, assert_env_vars, MissingCredsException, debug
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
import botocore

class TfStateStoreAwsS3(TfStateStore):
    s3_client = boto3.client('s3')

    def push(self):
        if not self.localpath_exists:
            return False
        bucket = self.args["bucket"]
        bucket_path = self.args["bucket_path"]
        try:
            response = self.s3_client.upload_file(
                self.localpath, bucket, "{}/terraform.tfvars".format(bucket_path))
        except ClientError as e:
            debug(e)
            return False
        return True

    def fetch(self):
        bucket = self.args["bucket"]
        bucket_path = self.args["bucket_path"]

        try:
            with open(self.localpath, 'wb') as fh:
                self.s3_client.download_fileobj(
                    bucket, '{}/terraform.tfvars'.format(bucket_path), fh)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                # tfstate is not found, touch a fresh one locally
                Path(self.localpath).touch()
                self.fetched = True
            elif e.response['Error']['Code'] == 403:
                raise
            else:
                # Something else has gone wrong.
                raise

        self.fetched = True

def aws_sts_cred_keys():
    return ["AWS_REGION", "AWS_ROLE_ARN", "AWS_ROLE_SESSION_NAME", "AWS_SESSION_TOKEN"]


def aws_cred_keys():
    return ["AWS_REGION", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]


def aws_test_creds():
    sts = boto3.client('sts',
                       aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", ""),
                       aws_secret_access_key=os.getenv(
                           "AWS_SECRET_ACCESS_KEY", "")
                       )
    try:
        sts.get_caller_identity()
        return True
    except:
        return False
    
def assert_aws_creds():

    if assert_env_vars(aws_sts_cred_keys()) == True:
        return True

    asserted = assert_env_vars(aws_cred_keys())

    if asserted == True:
        return True

    raise MissingCredsException(
        "Missing credentials in env vars: {}".format(", ".join(asserted)))
