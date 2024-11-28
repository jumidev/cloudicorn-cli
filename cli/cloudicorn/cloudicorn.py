#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
import argparse
from pyfiglet import Figlet
import git
from cloudicorn.core import runshow, log, flatwalk, git_check, hcldump, check_cloud_extension, list_cloud_extensions
from cloudicorn.core import Project, ProjectException
from cloudicorn.tfwrapper import WrapTerraform as WrapTf
from cloudicorn.tfwrapper import TFException
import importlib.metadata as im

if check_cloud_extension("opentofu"):
    from cloudicorn_opentofu import OpentofuUtils as Utils 
    from cloudicorn_opentofu import WrapOpentofu as WrapTf 
else:
    from cloudicorn.tfwrapper import Utils


PACKAGE = "cloudicorn"
LOG = True
DEBUG = False


def main(argv=[]):

    epilog = """The following arguments can be activated using environment variables:

    export CLOUDICORN_DEBUG=y                   # activates debug messages
    export CLOUDICORN_APPROVE=y                 # activates --yes
    export CLOUDICORN_GIT_CHECK=y               # activates --git-check
    export CLOUDICORN_GIT_FILTER                # when displaying components, only show those which have uncomitted git files
    export CLOUDICORN_TFSTATE_STORE_ENCRYPTION_PASSPHRASE #if set, passphrase to encrypt and decrypt remote state files at rest
    """
    # TGARGS=("--force", "-f", "-y", "--yes", "--clean", "--dev", "--no-check-git")

    f = Figlet(font='slant')

    backend_bin_name = "terraform"
    if check_cloud_extension("opentofu"):
        backend_bin_name = "opentofu"

    parser = argparse.ArgumentParser(description='{}\nCLOUDICORN, facilitates {} with nifty features n such.'.format(f.renderText('cloudicorn'), backend_bin_name),
                                     add_help=True,
                                     epilog=epilog,
                                     formatter_class=argparse.RawTextHelpFormatter)

    # parser.ArgumentParser(usage='Any text you want\n')

    # subtle bug in ArgumentParser... nargs='?' doesn't work if you parse something other than sys.argv,



    parser.add_argument('command', default=None, nargs='*',
                        help='command to run (apply, destroy, plan, etc)')

    parser.add_argument('--project-dir', default=None,
                        help='optional project root dir')
    parser.add_argument('--downstream-args', default=None,
                        help='optional arguments to pass downstream to {}'.format(backend_bin_name))
    parser.add_argument('--key', default=None,
                        help='optional remote state key to return')
    parser.add_argument('--set-var', action='append', nargs='+',
                        help='optional variable to override (usage: --set-var KEY=VALUE)')
    parser.add_argument('--python-wdir', default=None, help=argparse.SUPPRESS)
        

    parser.add_argument('--tf-bin-path', default=None,
                        help='specify path to {}'.format(backend_bin_name))
    parser.add_argument('--tfstate-store-encryption-passphrase', default=None,
                        help='specify encryption / decryption passphrase for tfstate store')
    # booleans
    parser.add_argument('--version', action='store_true', help='display cloudicorn version')
    parser.add_argument('--clean', dest='clean',
                        action='store_true', help='clear all cache')
    parser.add_argument('--force', '--yes', '-t', '-f', action='store_true',
                        help='Perform action without asking for confirmation (same as -auto-approve)')
    parser.add_argument('--dry', action='store_true',
                        help="dry run, don't actually do anything")
    parser.add_argument('--allow-no-tfstate-store', action='store_true',
                        help="allow components to be run without a tfstate_store block")
    parser.add_argument('--check-git', action='store_true',
                        help='Explicitly enable git repository checks')
    parser.add_argument('--git-filter', action='store_true',
                        help='when displaying components, only show those which have uncomitted files in them.')
    parser.add_argument('--quiet', "-q", action='store_true',
                        help='suppress output except fatal errors')
    parser.add_argument('--json', action='store_true',
                        help='When applicable, output in json format')
    parser.add_argument('--list', action='store_true',
                        help='list components in project')
    parser.add_argument('--setup', action='store_true',
                        help='Install binaries')
    parser.add_argument('--check-setup', action='store_true',
                        help='Check if binaries are up to date')
    parser.add_argument('--setup-shell', action='store_true',
                        help='Export a list of handy aliases to the shell.  Can be added to ~./bashrc')
    parser.add_argument('--debug', action='store_true',
                        help='display debug messages')

    args = parser.parse_args(args=argv)
    # TODO add project specific args to project.yml

    global LOG

    if args.quiet or args.json:
        LOG = False

    if args.debug or os.getenv('CLOUDICORN_DEBUG', 'n')[0].lower() in ['y', 't', '1']:
        global DEBUG
        DEBUG = True
        log("debug mode enabled")

    tf_path = args.tf_bin_path

    if args.python_wdir != None:
        # used for testing
        os.chdir(args.python_wdir)

    if "TERRAFORM_BIN" in os.environ:
        tf_path = os.getenv("TERRAFORM_BIN")

    if "OPENTOFU_BIN" in os.environ:
        tf_path = os.getenv("OPENTOFU_BIN")


   
    # (out, err, exitcode) = run("which terraform")
    # terraform_path = None
    # if exitcode == 0:
    #     terraform_path = out.strip()

    u = Utils(tf_path=tf_path)
    u.setup(args)

    if args.version:
        pypkg = 'cloudicorn-cli'

        build_date = "UNKNOWN"
        for k in im.metadata(pypkg)["Keywords"].split(" "):
            if k.startswith("build_date"):
                a,build_date = k.split(":")

        log("{} version {}".format(PACKAGE, im.version(pypkg)))
        log("build date: {}".format(build_date))
        ext = []
        for x,i in list_cloud_extensions():
            if i:
                
                ext.append(x+ " v"+im.version("cloudicorn-{}".format(x)))

        if len(ext) > 0:
            log("Extensions installed: {}".format(", ".join(ext)))

        runshow(u.tf_path+" version")
        return 0
    
    if args.setup_shell or args.check_setup or args.setup:
        return 0

    # grab args
    tfstate_store_encryption_passphrases = []
    if args.tfstate_store_encryption_passphrase != None:
        tfstate_store_encryption_passphrases.append(args.tfstate_store_encryption_passphrase)
    e = list(os.environ.keys())
    e.sort()

    for k in e:
        if k.startswith("CLOUDICORN_TFSTATE_STORE_ENCRYPTION_PASSPHRASE"):
            tfstate_store_encryption_passphrases.append(os.getenv(k))

    git_filtered = str(os.getenv('CLOUDICORN_GIT_FILTER',
                       args.git_filter)).lower() in ("on", "true", "1", "yes")
    force = str(os.getenv('CLOUDICORN_APPROVE', args.force)
                ).lower() in ("on", "true", "1", "yes")

    project_vars = {}

    if args.set_var != None:
        for set_var in args.set_var:
            k, v = set_var[0].split("=", 1)
            project_vars[k] = v

    project = Project(git_filtered=git_filtered, project_vars=project_vars, wdir=args.project_dir)
    
    # incorrect project dir specified in args
    if args.project_dir != None and not project.check_project_dir():
        raise ProjectException("{} is not a cloudicorn project".format(args.project_dir))

    if not project.check_project_dir():
        # project-dir not explicitly specified in args
        try:
            try:
                # component provided
                cdir = args.command[2]
                try:
                    folder, component_reldir = project.find_project_root(cdir)

                    # found project dir, set it
                    project.wdir=folder

                    # update cdir to point to component relative to newly found
                    # project root
                    args.command[2] = component_reldir
                    cdir = component_reldir

                except ProjectException:
                    folder, reldir = project.find_project_root()
                    if os.path.abspath(os.getcwd()).startswith(project.project_root):
                        # cwd is a subdir of project
                        project.wdir=folder
                        cdir2 = os.path.join(reldir, cdir)
                        args.command[2] = cdir2
                        cdir = cdir2

                    else:
                        raise

            except IndexError:
                # no component provided
                folder, component_reldir = project.find_project_root()
                project.wdir=folder
          
        except:
            raise ProjectException("{} does not appear to be a cloudicorn project".format(project.project_root))

    wt = WrapTf(tf_path=u.tf_path)
    project.set_passphrases(tfstate_store_encryption_passphrases)

    if args.downstream_args != None:
        wt.set_option(args.downstream_args)

    if len(args.command) < 2:

        if args.list:
            for which, component, match in project.get_components():
                print(component)
            return 0

        log("ERROR: no command specified, see help")
        return (-1)
    else:
        command = args.command[1]

    if command == backend_bin_name:
        print(u.tf_path)
        return 0

    CHECK_GIT = False

    if args.check_git or os.getenv('CLOUDICORN_GIT_CHECK', 'n')[0].lower() in ['y', 't', '1']:
        CHECK_GIT = True

    # check git
    if CHECK_GIT:
        try:
            gitstatus = git_check()
            if gitstatus != 0:
                return gitstatus
        except git.exc.GitCommandError:
            pass
    
    # TODO add "env" command to show the env vars with optional --export command for exporting to bash env vars

    if command == "format":
        for (dirpath, filename) in flatwalk('.'):
            if filename.endswith('.hclt'):
                project.format_hclt_file("{}/{}".format(dirpath, filename))

    # if command == "parse":
    #     try:
    #         wdir = os.path.relpath(args.command[2])
    #     except:
    #         # no component provided, loop over all and parse them

    if command in ("plan", "apply", "destroy", "refresh", "show", "force-unlock", "parse", "showvars"):

        try:
            cdir = args.command[2]
        except IndexError:
            # provide list of components relative to cwd
            log("OOPS, no component specified, try one of these (bundles are <u><b>bold underlined</b>):")

            prefix = ""
            if os.path.abspath(os.getcwd()) != project.project_root:
                if os.path.abspath(os.getcwd()).startswith(project.project_root):
                    # cwd is a subdir of project
                    prefix = os.path.relpath(os.path.abspath(os.getcwd()), project.project_root)+"/"

            for which, component, match in project.get_components():
                if match and component.startswith(prefix):
                    s = "{} {} {}".format(PACKAGE, command, component[len(prefix):])
                    if which == "bundle":
                        s = "{} {} <u><b>{}</u>".format(PACKAGE,
                                                        command, component)
                    log(s)
            log("")
            
            return (100)

        if not os.path.isdir(os.path.join(project.wdir, cdir)):
            log("ERROR: {} is not a directory".format(cdir))
            return -1

        # project.set_component_dir(cdir)

        # cdir_slug = cdir.replace('/', '_')
        # tf_wdir_p = get_cloudicorn_cachedir(project.project_root+cdir_slug)

        # tf_wdir = '{}/{}'.format(tf_wdir_p, cdir_slug)
        # os.makedirs(tf_wdir)

        # debug("setting tf_wdir to {}".format(tf_wdir))
        # project.set_tf_dir(tf_wdir)

        # -auto-approve and refresh|plan do not mix
        if command in ["refresh", "plan"]:
            force = False

        if force:
            wt.set_option("-auto-approve")

        if args.quiet:
            wt.set_quiet()

        t = project.component_type(component=cdir)
        if t == "component":
            project.set_component_dir(cdir)
            project.parse_component()
            retcode = handle_component(project, command, args, wt, u, tfstate_store_encryption_passphrases, True)
            return retcode

        elif t == "bundle":
            log("Performing {} on bundle {}".format(command, cdir))
            log("")
            # parse first
            parse_status = []
            components = project.get_bundle(cdir)

            for component in components:

                project.set_component_dir(component)
                project.parse_component()
                project.save_parsed_component()
                if project.parse_status != True:

                    parse_status.append(project.parse_status)

            if len(parse_status) > 0:
                print("\n".join(parse_status))
                return (120)

            if command == "parse":
                # we have parsed, our job here is done
                return 0

            if command == "destroy":
                # destroy in opposite order
                components.reverse()

            # run per component
            retcode = None
            for component in components:
                project.set_component_dir(component)
                retcode = handle_component(project, command, args, wt, u, tfstate_store_encryption_passphrases, False)
                if retcode != 0:
                    # stop right here
                    return retcode

            return retcode
                

        else:
            log("ERROR {}: this directory is neither a component nor a bundle, nothing to do".format(cdir))
            return 130


def handle_component(project: Project, command : str, args, wt: WrapTf, u: Utils, tfstate_store_encryption_passphrases : list=[], showrun : bool=False):
    project.save_parsed_component()

    if command == "showvars":
        if args.json:
            print(json.dumps(project.vars, indent=4))
        else:
            keys = list(project.vars.keys())  # .sorted()
            keys.sort()
            for k in keys:
                print("{}={}".format(k, project.vars[k]))
            # print(json.dumps(project.vars, indent=4))
        return 0

    if project.parse_status != True:
        print(project.parse_status)
        return (120)

    if command == "parse":
        # we have parsed, our job here is done
        return 0

    check = project.check_parsed_file(
        require_tfstate_store_block=not args.allow_no_tfstate_store)
    if check != True:
        print("An error was found after parsing {}: {}".format(
            project.outfile, check))
        return 110

    if args.key != None:
        project.setup_component_tfstore()
        # rs = TfStateReader()
        print(project.component.get_output(args.key))
        return 0
    else:
        if args.json:
            wt.set_option('-json')
            wt.set_option('-no-color')

        if not args.dry:
            project.setup_component_source()

            project.setup_component_file_overrides()

            tfvars_hcl = hcldump(project.component_inputs)
            with open("{}/terraform.tfvars".format(project.tf_dir), "w") as fh:
                fh.write(tfvars_hcl)

            # init
            cmd = "{} init ".format(u.tf_path)

            if showrun:
                exitcode = runshow(cmd, cwd=project.tf_dir)
            else:
                exitcode = runshow(cmd, cwd=project.tf_dir, stdout=None, stderr=None)

            if exitcode != 0:
                raise TFException(
                    "\ndir={}\ncmd={}".format(project.tf_dir, cmd))

            # requested command
            extra_args = ['-state=terraform.tfstate']

            cmd = wt.get_command(command, extra_args)

            if showrun:
                exitcode = runshow(cmd, cwd=project.tf_dir)
            else:
                exitcode = runshow(cmd, cwd=project.tf_dir, stdout=None, stderr=None)

            # our work is done here
            if command in ["refresh", "plan"]:
                return 0

            crs = project.componenttfstore
            if tfstate_store_encryption_passphrases != []:
                crs.set_passphrases(
                    tfstate_store_encryption_passphrases)
                crs.encrypt()

            # save tfstate
            crs.push()
            if exitcode != 0:
                raise TFException(
                    "\ndir={}\ncmd={}".format(project.tf_dir, cmd))

    return 0


def cli_entrypoint():
    retcode = main(sys.argv)
    exit(retcode)


if __name__ == '__main__':
    retcode = main(sys.argv)
    exit(retcode)
