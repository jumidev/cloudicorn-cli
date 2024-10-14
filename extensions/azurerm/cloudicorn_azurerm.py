#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from datetime import datetime, timedelta

from cloudicorn.core import TfStateStore, MissingCredsException, assert_env_vars
from pathlib import Path

from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from azure.identity import EnvironmentCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import ResourceNotFoundError

class AzureUtils():

    def __init__(self) -> None:
        self.creds = None
        self.rmc = None
        self.smc = None

    @property
    def credential(self):
        if self.creds == None:
            self.creds = EnvironmentCredential()

        return self.creds

    @property
    def subscription_id(self):
        return os.environ["AZURE_SUBSCRIPTION_ID"]

    @property
    def resource_client(self):
        if self.rmc == None:
            self.rmc = ResourceManagementClient(
                self.credential,  self.subscription_id)

        return self.rmc

    @property
    def storage_management_client(self):
        if self.smc == None:
            self.smc = StorageManagementClient(
                self.credential,  self.subscription_id)

        return self.smc

    def get_storage_account(self, name):
        resourcelist = self.resource_client.resource_groups.list()
        for rg in resourcelist:
            for res in self.resource_client.resources.list_by_resource_group(rg.name):
                if (res.type == 'Microsoft.Storage/storageAccounts'):
                    if res.name == name:
                        return (rg.name, res.name)

    def get_storage_account_key(self, name):
        (rg, name) = self.get_storage_account(name)

        keys = self.storage_management_client.storage_accounts.list_keys(
            rg,  name)

        return keys.keys[0].value

    def generate_sas_token(self, storage_account_name, container, blob_path, valid_hours=1):
        account_key = self.get_storage_account_key(storage_account_name)
        token = generate_blob_sas(
            account_name=storage_account_name,
            account_key=account_key,
            container_name=container,
            blob_name=blob_path,
            permission=BlobSasPermissions(read=True, write=True, create=True),
            expiry=datetime.utcnow() + timedelta(hours=valid_hours),
        )
        return token


class TfStateStoreAzureStorage(TfStateStore):

    def __init__(self, args, localpath) -> None:
        super().__init__(args, localpath)
        self.token = None

    azure_utils = AzureUtils()

    @property
    def sas_token(self):
        if self.token == None:
            container_path = self.args["container_path"]
            account = self.args["storage_account"]
            container = self.args["container"]
            blob_path = '{}/terraform.tfvars'.format(container_path)

            self.token = self.azure_utils.generate_sas_token(
                account, container, blob_path)

        return self.token

    @property
    def az_blob_client(self):
        account = self.args["storage_account"]
        account_url = "{}.blob.core.windows.net".format(account)
        container_path = self.args["container_path"]
        blob_path = '{}/terraform.tfvars'.format(container_path)

        blob_service_client = BlobServiceClient(
            account_url=account_url, credential=self.sas_token)
        container_name = self.args["container"]
        return blob_service_client.get_blob_client(container=container_name, blob=blob_path)

    def fetch(self):
        # https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-download-python#download-to-a-stream

        blob_client = self.az_blob_client
        try:
            downloader = blob_client.download_blob(
                max_concurrency=1, encoding='UTF-8')
            blob_text = downloader.readall()

            with open(self.localpath, 'w') as fh:
                fh.write(blob_text)

            self.fetched = True
        except ResourceNotFoundError:
            Path(self.localpath).touch()
            self.fetched = True

    def push(self):
        if not self.localpath_exists:
            return False

        # https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-download-python#download-to-a-stream
        blob_client = self.az_blob_client

        container_path = self.args["container_path"]
        blob_path = '{}/terraform.tfvars'.format(container_path)

        with open(self.localpath, 'rb') as fh:
            blob_client.upload_blob(data=fh, overwrite=True)

def azurerm_sp_cred_keys():
    return ["AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID", "AZURE_SUBSCRIPTION_ID"]


def assert_azurerm_sp_creds():
    asserted = assert_env_vars(azurerm_sp_cred_keys())
    if asserted == True:
        return True

    raise MissingCredsException(
        "Missing credentials in env vars: {}".format(", ".join(asserted)))
