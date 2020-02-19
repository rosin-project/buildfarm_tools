#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2019 Tecnalia Research and Innovation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ruamel.yaml.scalarstring import SingleQuotedScalarString
from ruamel.yaml import YAML
from pathlib import Path

import datetime
import os
import tempfile
from flaskr.configure_buildfarm_config import Generator
from flaskr.gitwrapper import GitWrapper
import urllib
from urllib.parse import urlparse


# todo this class could be removed depending on whether we want to use or not.
class BuildfarmData(object):
    def __init__(self):
        self.ssh_private = ''
        self.ssh_public = ''
        self.ip_master = ''
        self.ip_repo = ''
        self.timezone = ''
        self.jenkins_user = ''
        self.jenkins_password = ''
        self.repo_hostkey = ''
        self.gpg_key_id = ''
        self.gpg_private_key = ''
        self.gpg_public_key = ''
        self.architectures = []
        self.distros = []

    def __str__(self):
        msg = "Instance of BuildfarmData class: { \n"

        msg += "  ssh_private = {}\n".format(self.ssh_private)
        msg += "  ssh_public = {}\n".format(self.ssh_public)
        msg += "  ip_master = {}\n".format(self.ip_master)
        msg += "  ip_repo = {}\n".format(self.ip_repo)
        msg += "  timezone = {}\n".format(self.timezone)
        msg += "  jenkins_user = {}\n".format(self.jenkins_user)
        msg += "  jenkins_password = {}\n".format(self.jenkins_password)
        msg += "  repo_hostkey = {}\n".format(self.repo_hostkey)
        msg += "  gpg_key_id = {}\n".format(self.gpg_key_id)
        msg += "  gpg_private_key = {}\n".format(self.gpg_private_key)
        msg += "  gpg_public_key = {}\n".format(self.gpg_public_key)
        msg += "  architectures = {}\n".format(self.architectures)
        msg += "  distros = {}\n".format(self.distros)

        msg += "}"
        return msg


class BuildFarmConfigData(object):
    def __init__(self):

        # Parameter read from the buildfarm deploy config
        self.ssh_private = ''
        self.ssh_public = ''
        self.ip_master = ''
        self.ip_repo = ''
        self.timezone = ''
        self.jenkins_user = ''
        self.jenkins_password = ''
        self.repo_hostkey = ''
        self.gpg_key_id = ''
        self.gpg_private_key = ''
        self.gpg_public_key = ''
        self.architectures = list()
        self.distros = list()

        self.ros_distros = list()

        # Additional parameters added from interaction with user
        self.distro_model = ''
        self.addon_tag = ''
        self.email_buildfarm = ''
        self.rosdistro_index_url = ''
        self.config_repo = ''
        self.config_branch = ''
        self.config_filename = '/tmp/buildfarm_cfg/config_wizard.cfg'
        self.folder_generated = ''

    def load_build_config(self, filename):
        print('opening file {}'.format(filename))

        dictname = filename.read()
        dictname = eval(dictname)

        self.ssh_private = SingleQuotedScalarString(dictname['ssh_private'])
        self.ssh_public = dictname['ssh_public']
        self.ip_master = dictname['ip_master']
        self.ip_repo = dictname['ip_repo']
        self.timezone = dictname['timezone']
        self.jenkins_user = dictname['jenkins_user']
        self.jenkins_password = dictname['jenkins_password']
        self.repo_hostkey = dictname['repo_hostkey']
        self.gpg_key_id = dictname['gpg_key_id']
        self.gpg_private_key = SingleQuotedScalarString(dictname['gpg_private_key'])
        self.gpg_public_key = SingleQuotedScalarString(dictname['gpg_public_key'])
        self.architectures = dictname['architectures']
        self.distros = dictname['distros']
        self.git_fetch_ssh_id = dictname['git_fetch_ssh_id']

        all_ros_distros = [item['ros'] for item in self.distros]
        # creating a dict enables removing duplaicated entries.
        self.ros_distros = sorted(list(dict.fromkeys(all_ros_distros)))

        return True

    def load_complete_config(self, filename):
        print('opening file {}'.format(filename))

        try:
            with open(filename, 'r') as open_file:
                dictname = open_file.read()
            dictname = eval(dictname)

            # data related to the deploy setup
            self.ssh_private = dictname['ssh_private']
            self.ssh_public = dictname['ssh_public']
            self.ip_master = dictname['ip_master']
            self.ip_repo = dictname['ip_repo']
            self.timezone = dictname['timezone']
            self.jenkins_user = dictname['jenkins_user']
            self.jenkins_password = dictname['jenkins_password']
            self.repo_hostkey = dictname['repo_hostkey']
            self.gpg_key_id = dictname['gpg_key_id']
            self.gpg_private_key = dictname['gpg_private_key']
            self.gpg_public_key = dictname['gpg_public_key']
            self.architectures = dictname['architectures']
            self.distros = dictname['distros']
            self.git_fetch_ssh_id = dictname['git_fetch_ssh_id']

            # data related to the config setup
            self.distro_model = dictname['distro_model']
            self.addon_tag = dictname['addon_tag']
            self.email_buildfarm = dictname['email_buildfarm']
            self.rosdistro_index_url = dictname['rosdistro_index_url']
            self.config_repo = dictname['config_repo']
            self.config_branch = dictname['config_branch']

            # additional data added for convenience

            all_ros_distros = [item['ros'] for item in self.distros]
            # creating a dict enables removing duplaicated entries.
            self.ros_distros = sorted(list(dict.fromkeys(all_ros_distros)))

        except FileNotFoundError as err:
            print("Could not open file {}: {}".format(filename, err))
            return False
        except KeyError as err:
            print("Missing expected tag in {}: {}".format(filename, err))
            return False
        print("Configuration load done with success")
        return True

    def store(self):

        local_dir = tempfile.mkdtemp()
        self.config_filename = local_dir + "/" + os.path.basename(self.config_filename)

        with open(self.config_filename, "w") as f:
            f.write(str(self.__dict__))

        print("Configuration saved in {}".format(self.config_filename))
        return True

    def generate_files(self):
        # create folder to store generated file
        self.folder_generated = tempfile.mkdtemp()

        # instanciate the junja component
        generator = Generator("flaskr/rosdistro_template", self.folder_generated)
        # generate the local repository
        print("Generate common files")
        if not generator.generate_all(self.config_filename):
            print("Error during the generation process")
            return False
        print("Generate distribution files")
        if not generator.generate_distributions():
            print("Error during the generation process")
            return False
        print("Config content generated")

        return True

    def update_repo(self, username, password):
        # copy it to the requested repository.
        print("Pushing the result to the indicated repository")
        print(self.config_repo)
        cfg_repo_handler = GitWrapper()

        # check if authentification is required.

        url_parsed = urlparse(self.config_repo)
        is_credential = url_parsed.scheme in ['http', 'https']
        # print(url_parsed)
        tmp_url = self.config_repo
        if is_credential:
            tmp_url = (
                url_parsed.scheme
                + "://"
                + urllib.parse.quote(username)
                + ":"
                + urllib.parse.quote(password)
                + "@"
                + url_parsed.netloc
                + url_parsed.path
            )

        directory_name_rep = tempfile.mkdtemp()

        if not cfg_repo_handler.clone(tmp_url,
                                      self.config_branch,
                                      directory_name_rep):
            print("Could not clone")
            return False

        print("Repository locally cloned")
        print("Deploying material")

        if not cfg_repo_handler.deploy_content(self.folder_generated,
                                               "wizard-based commit "):
            print("Error during deployment")
            return False

        print("Repo updated")
        return True

    def get_config_repo_raw(self):
        str_url = str(self.config_repo)
        print("Working with {}".format(str_url))

        # take out the final .git
        str_url = str_url[:-4]
        print("step 1: {}".format(str_url))
        # check for github repo
        if 'github.com' in str_url:
            str_https = "https://github.com/"
            if str_url.startswith(str_https):
                str_url = str_url[len(str_https):]
            str_ssh = "git@github.com:"
            if str_url.startswith(str_ssh):
                str_url = str_url[len(str_ssh):]

            str_url = 'https://raw.githubusercontent.com/' + str_url
            str_url += "/master/index.yaml"

            print("raw_url: {}".format(str_url))
            return str_url

        # check for gitlab repo
        if 'gitlab.com' in str_url:
            str_ssh = "git@gitlab.com:"
            if str_url.startswith(str_ssh):
                str_url = str_url[len(str_ssh):]
                str_url = "https://gitlab.com/" + str_url
            str_url += "/raw/master/index.yaml"

            print("raw_url: {}".format(str_url))
            return str_url

        return None
