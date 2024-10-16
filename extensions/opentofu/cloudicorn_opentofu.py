

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cloudicorn.core import debug, log, run, download_progress
from cloudicorn.tfwrapper import TFWrapper, TFException
import os
import hashlib
import requests
import hcl
import json
import zipfile
import time


class WrapOpentofu(TFWrapper):
    def __init__(self, bin_path=None):

        if bin_path == None:
            bin_path = os.getenv("OPENTOFU_BIN", "opentofu")

        self.tf_bin = bin_path
        self.cli_options = []
        self.quiet = False

class Utils():

    conf_dir = os.path.expanduser("~/.config/cloudicorn")
    bin_dir = os.path.expanduser("~/.config/cloudicorn/bin")

    def __init__(self, tf_path=None):
        self.tf_v = None

        conf_file = "{}/config.hcl".format(self.conf_dir)
        if os.path.isfile(conf_file):
            with open(conf_file, 'r') as fp:
                self.conf = hcl.load(fp)
        else:
            self.conf = {}

        try:
            self.bin_dir = os.path.expanduser(self.conf['bin_dir'])
        except:
            pass
        if tf_path == None:
            tf_path = os.getenv("TERRAFORM_BIN", None)
        if tf_path == None:
            tf_path = "{}/terraform".format(self.bin_dir)
            if not os.path.isdir(self.bin_dir):
                os.makedirs(self.bin_dir)

        self.terraform_path = tf_path

        if not os.path.isdir(self.conf_dir):
            os.makedirs(self.conf_dir)

    def terraform_currentversion(self):
        if self.tf_v == None:
            r = requests.get(
                "https://releases.hashicorp.com/terraform/index.json")
            obj = json.loads(r.content)
            versions = []
            for k in obj['versions'].keys():
                a, b, c = k.split('.')

                try:
                    v1 = "{:05}".format(int(a))
                    v2 = "{:05}".format(int(b))
                    v3 = "{:05}".format(int(c))
                    versions.append("{}.{}.{}".format(v1, v2, v3))
                except ValueError:
                    # if alphanumeric chars in version
                    # this excludes, rc, alpha, beta versions
                    continue

            versions.sort()  # newest will be at the end
            v1, v2, v3 = versions.pop(-1).split(".")

            latest = "{}.{}.{}".format(int(v1), int(v2), int(v3))

            url = "https://releases.hashicorp.com/terraform/{}/terraform_{}_linux_amd64.zip".format(
                latest, latest)

            self.tf_v = (latest, url)

        return self.tf_v

    def install(self, update=True):
        debug("install")
        missing, outofdate = self.check_setup(verbose=False, updates=True)

        debug("missing={}".format(missing))
        debug("outofdate={}".format(outofdate))

        if len(missing)+len(outofdate) == 0:
            log("SETUP, Nothing to do. terraform installed and up to date")
        else:
            if "terraform" in missing:
                log("Installing terraform")
                self.install_terraform()
            elif "terraform" in outofdate and update:
                log("Updating terraform")
                self.install_terraform()

    def install_terraform(self, version=None):
        currentver, url = self.terraform_currentversion()
        if version == None:
            version = currentver

        log("Downloading terraform {} to {}...".format(
            version, self.terraform_path))
        download_progress(url, self.terraform_path+".zip")

        with zipfile.ZipFile(self.terraform_path+".zip", 'r') as zip_ref:
            zip_ref.extract("terraform", os.path.abspath(
                '{}/../'.format(self.terraform_path)))

        os.chmod(self.terraform_path, 500)  # make executable
        os.unlink(self.terraform_path+".zip")  # delete zip

    def check_setup(self, verbose=True, updates=True):
        missing = []
        outofdate = []
        debug(self.terraform_path)
        out, err, retcode = run("{} --version".format(self.terraform_path))

        debug("check setup")
        debug((out, err, retcode))

        if retcode == 127:
            missing.append("terraform")
            if verbose:
                log("terraform not installed, you can download it from https://www.terraform.io/downloads.html")
        elif "Your version of Terraform is out of date" in out and updates:
            outofdate.append("terraform")
            if verbose:
                log("Your version of terraform is out of date! You can update by running 'cloudicorn_setup', or by manually downloading from https://www.terraform.io/downloads.html")

        return (missing, outofdate)

    def autocheck(self, hours=8):
        check_file = "{}/autocheck_timestamp".format(self.conf_dir)
        if not os.path.isfile(check_file):
            diff = hours*60*60  # 8 hours
        else:
            last_check = int(os.stat(check_file).st_mtime)
            diff = int(time.time() - last_check)

        updates = False
        if diff >= hours*60*60:
            updates = True
            if os.path.isfile(check_file):
                '''
                The previous check file has expired, we want to delete it so that it will be recreated in the block below
                '''
                os.unlink(check_file)

        else:
            debug("last check {} hours ago".format(float(diff)/3600))

        missing, outdated = self.check_setup(verbose=True, updates=updates)
        if len(missing) > 0:
            return -1

        if len(outdated) == 0 and not os.path.isfile(check_file):
            '''
            since checking for updates takes a few seconds, we only want to do this once every 8 hours
            HOWEVER, once the update is available, we want to inform the user on EVERY EXEC, since they might
            not see the prompt immediately. 
            '''
            with open(check_file, "w") as fh:
                pass  # check again in 8 hours

    def setup(self, args):
        debug("setup")

        if args.setup:
            self.install()

        if args.check_setup:
            missing, outdated = self.check_setup()

            if len(missing) > 0:
                log("CHECK SETUP: MISSING {}".format(", ".join(missing)))

            elif len(outdated) > 0:
                log("CHECK SETUP: UPDATES AVAILABLE")
            else:
                log("terraform installed and up to date")

        else:
            # auto check once every 8 hours
            self.autocheck()

        if args.setup_shell:
            with open(os.path.expanduser('~/.bashrc'), 'r') as fh:
                bashrc = fh.readlines()

            lines = (
                "alias cloudi_y='export CLOUDICORN_APPROVE=true'",
                "alias cloudi_n='export CLOUDICORN_APPROVE=false'",
                "alias cloudi_gf='export CLOUDICORN_GIT_FILTER=true'",
                "alias cloudi_gfn='export CLOUDICORN_GIT_FILTER=false'")

            with open(os.path.expanduser('~/.bashrc'), "a") as fh:
                for l in lines:
                    l = "{}\n".format(l)
                    if l not in bashrc:
                        fh.write(l)
            log("SETUP SHELL: OK")
