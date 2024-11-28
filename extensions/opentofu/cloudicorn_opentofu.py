#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cloudicorn.core import debug, log, run, download_progress
from cloudicorn.tfwrapper import TFWrapper, Utils
import os
import hashlib
import requests
import hcl
import json
import zipfile
import time
import platform as plat

from prompt_toolkit.shortcuts import yes_no_dialog
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.formatted_text import HTML

class WrapOpentofu(TFWrapper):
    pass

def get_release(v):
    from sys import platform
    p = plat.machine()

    if p == "x86_64":
        arch = "amd64"
    if p == "aarch64":
        arch = "arm64"

    dlroot = "https://github.com/opentofu/opentofu/releases/download"
    return "{}/{}/tofu_{}_{}_{}.zip".format(dlroot, v, v[1:], platform, arch)


class OpentofuUtils(Utils):

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

            tf_path = "{}/tofu".format(self.bin_dir)
            if not os.path.isdir(self.bin_dir):
                os.makedirs(self.bin_dir)

        self.tf_path = tf_path
        
        if not os.path.isdir(self.conf_dir):
            os.makedirs(self.conf_dir)

    def tf_currentversion(self):
        if self.tf_v == None:
            r = requests.get("https://github.com/opentofu/opentofu/releases/latest")
            v = r.url.split("/")[-1]

            dl_url = get_release(v)

            self.tf_v = (v, dl_url)

        return self.tf_v

    def install(self, update=True):
        debug("install")
        missing, outofdate = self.check_setup(verbose=False, updates=True)

        debug("missing={}".format(missing))
        debug("outofdate={}".format(outofdate))

        if missing:
            log("Installing opentofu")
            self.install_opentofu()
        elif outofdate:
            if update:
                log("Updating opentofu")
                self.install_opentofu()
            else:
                log("An update is available for opentofu")
        else:
            log("SETUP, Nothing to do. opentofu installed and up to date")

    def install_opentofu(self, version=None):
        currentver, url = self.tf_currentversion()
        if version == None:
            version = currentver

        log("Downloading opentofu {} to {}...".format(
            version, self.tf_path))
        download_progress(url, self.tf_path+".zip")

        with zipfile.ZipFile(self.tf_path+".zip", 'r') as zip_ref:
            zip_ref.extract("tofu", os.path.abspath(
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
                log("opentofu not installed, you can download it from https://github.com/opentofu/opentofu/releases")
        elif "Your version of Opentofu is out of date" in out and updates:
            outofdate = True
            if verbose:
                log("Your version of opentofu is out of date! You can update by running 'cloudicorn_setup', or by manually downloading from https://github.com/opentofu/opentofu/releases")

        return missing, outofdate

    def autocheck(self, hours=8):
        check_file = "{}/opentofu_autocheck_timestamp".format(self.conf_dir)
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
                log("CHECK SETUP: MISSING {}".format(", ".join(missing)))

            elif outdated:
                log("CHECK SETUP: UPDATES AVAILABLE")
            else:
                log("opentofu installed and up to date")

        else:
            # auto check once every 8 hours
            self.autocheck()


    def setuptui(self):
        try:
            missing, outdated = self.check_setup()
            self.tf_currentversion()
            if missing:
                self.install_opentofu()
                ok = message_dialog(
                    title='Success',
                    text='opentofu {} successfully installed.'.format(self.tf_currentversion()[0])).run()
            elif outdated:
                ans = yes_no_dialog(
                    title='{} is out of date'.format("opentofu"),
                    text='upgrade to latest version?').run()
                if ans:
                    self.install_opentofu()
            else:
                ok = message_dialog(
                    title='Nothing to do',
                    text='opentofu {} is already installed in {} and is the latest version.'.format(self.tf_currentversion()[0], self.tf_path)).run()

            rcfile = os.path.expanduser('~/.tofurc')
            plugin_cache = False

            lines = []

            if os.path.isfile(rcfile):
                with open(rcfile, 'r') as fh:
                    for line in fh.readlines():
                        lines.append(line)
                        if "plugin_cache_dir = " in line:
                            plugin_cache = True

            if not plugin_cache:
                ans = yes_no_dialog(
                    title='No opentofu plugin cache',
                    text='No opentofu plugin cache found in ~/.tofurc.  Caching plugins locally saves bandwidth and reduces init time.  Enable caching?').run()
                if ans:
                    plugin_cache_dir = os.path.expanduser("~/.tofu.d/plugin-cache")
                    lines.append(
                        'plugin_cache_dir = "{}"'.format(plugin_cache_dir))

                    with open(rcfile, "w") as fh:
                        for l in lines:
                            fh.write(l)
                    d = os.path.expanduser(plugin_cache_dir)
                    if not os.path.isdir(d):
                        os.makedirs(d)


        except Exception as e:
            ok = message_dialog(
                title='Error',
                text='Could not check {}\n {}.'.format("opentofu", str(e))).run()
