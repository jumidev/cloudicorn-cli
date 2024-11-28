#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cloudicorn.core import debug, log, run, download_progress
import os
import hashlib
import requests
import hcl
import json
import zipfile
import time

from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.formatted_text import HTML

class TFException(Exception):
    pass


class TFWrapper():

    def __init__(self, tf_path):

        self.tf_path = tf_path
        self.cli_options = []
        self.quiet = False

    def get_cache_dir(ymlfile, package_name):
        cache_slug = os.path.abspath(ymlfile)
        debug("cache_slug = {}".format(cache_slug))
        return os.path.expanduser('~/.{}_cache/{}'.format(package_name, hashlib.sha224(cache_slug).hexdigest()))

    def set_option(self, option):
        self.cli_options.append(option)

    def set_quiet(self, which=True):
        self.quiet = which

    def get_command(self, command, extra_args=[]):

        cmd = "{} {} {} {}".format(self.tf_path, command, " ".join(
            set(self.cli_options)), " ".join(extra_args))

        if self.quiet:
            cmd += " > /dev/null 2>&1 "

        debug("running command:\n{}".format(cmd))
        return cmd

class WrapTerraform(TFWrapper):
    pass

class Utils():

    conf_dir = os.path.expanduser("~/.config/cloudicorn")
    bin_dir = os.path.expanduser("~/.config/cloudicorn/bin")

    def __init__(self, tf_path=None):
        self.tf_v = None

        if tf_path == None:
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

            tf_path = "{}/terraform".format(self.bin_dir)
            if not os.path.isdir(self.bin_dir):
                os.makedirs(self.bin_dir)

        self.tf_path = tf_path
        
        if not os.path.isdir(self.conf_dir):
            os.makedirs(self.conf_dir)

    def tf_currentversion(self):
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

        if missing:
            log("Installing terraform")
            self.install_terraform()
        elif outofdate:
            if update:
                log("Updating terraform")
                self.install_terraform()
            else:
                log("An update is available for terraform")
        else:
            log("SETUP, Nothing to do. terraform installed and up to date")

    def install_terraform(self, version=None):
        currentver, url = self.tf_currentversion()
        if version == None:
            version = currentver

        log("Downloading terraform {} to {}...".format(
            version, self.tf_path))
        download_progress(url, self.tf_path+".zip")

        with zipfile.ZipFile(self.tf_path+".zip", 'r') as zip_ref:
            zip_ref.extract("terraform", os.path.abspath(
                '{}/../'.format(self.tf_path)))

        os.chmod(self.tf_path, 500)  # make executable
        os.unlink(self.tf_path+".zip")  # delete zip

    def check_setup(self, verbose=True, updates=True):
        missing = False
        outofdate = False
        debug(self.tf_path)
        out, err, retcode = run("{} --version".format(self.tf_path))

        debug("check setup")
        debug((out, err, retcode))

        if retcode == 127:
            missing = True
            if verbose:
                log("terraform not installed, you can download it from https://www.terraform.io/downloads.html")
        elif "Your version of Terraform is out of date" in out and updates:
            outofdate = True
            if verbose:
                log("Your version of terraform is out of date! You can update by running 'cloudicorn_setup', or by manually downloading from https://www.terraform.io/downloads.html")

        return missing, outofdate

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
        if missing:
            return -1

        if not outdated and not os.path.isfile(check_file):
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

            if missing:
                log("CHECK SETUP: terraform not installed")

            elif outdated:
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

    def setuptui(self):
        try:
            missing, outdated = self.check_setup()
            self.tf_currentversion()
            if missing:
                self.install_terraform()
                ok = message_dialog(
                    title='Success',
                    text='terraform {} successfully installed.'.format(self.tf_currentversion()[0])).run()
            elif outdated:
                ans = yes_no_dialog(
                    title='{} is out of date'.format("terraform"),
                    text='upgrade to latest version?').run()
                if ans:
                    self.install_terraform()
            else:
                ok = message_dialog(
                    title='Nothing to do',
                    text='terraform {} is already installed in {} and is the latest version.'.format(self.tf_currentversion()[0], self.tf_path)).run()

            terraformrc = os.path.expanduser('~/.terraformrc')
            plugin_cache = False

            lines = []

            if os.path.isfile(terraformrc):
                with open(terraformrc, 'r') as fh:
                    for line in fh.readlines():
                        lines.append(line)
                        if "plugin_cache_dir = " in line:
                            plugin_cache = True

            if not plugin_cache:
                ans = yes_no_dialog(
                    title='No terraform plugin cache',
                    text='No terraform plugin cache found in ~/.terraformrc.  Caching terraform plugins locally saves bandwidth and reduces init time.  Enable caching?').run()
                if ans:
                    lines.append(
                        'plugin_cache_dir = "$HOME/.terraform.d/plugin-cache"')

                    with open(terraformrc, "w") as fh:
                        for l in lines:
                            fh.write(l)

        except Exception as e:
            ok = message_dialog(
                title='Error',
                text='Could not check {}\n {}.'.format("terraform", str(e))).run()
