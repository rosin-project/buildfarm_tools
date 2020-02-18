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

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import PreservedScalarString
from ruamel.yaml.scalarstring import SingleQuotedScalarString
from pathlib import Path
import os
from bcrypt import hashpw, gensalt
from flaskr.forms import SummaryForm


class BuildfarmData:
    def __init__(self, filename=None):
        if not filename:
            self.ssh_name = ''
            self.ssh_type = ''
            self.ssh_private = ''
            self.ssh_public = ''
            self.git_fetch_ssh_username = ''
            self.git_fetch_ssh_id = ''
            self.git_fetch_ssh_passphrase = ''
            self.git_fetch_ssh_private_key = ''
            self.git_fetch_hostkey = ''
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
            self.ubuntu_distros = []
            # path to which is stored the configuration file
            self.config_filename = '/tmp/buildfarm_cfg/deploy_wizard.cfg'
        else:
            print('opening file {}'.format(filename))
            with open(filename, 'r') as open_file:
                dictname = open_file.read()
            dictname = eval(dictname)
            for key in dictname:
                print("setting key {}".format(key))
                setattr(self, key, dictname[key])

    def to_yaml(self):
        self.ubuntu_distros = [x['ubuntu'] for x in self.distros]
        self.ubuntu_distros = list(set(self.ubuntu_distros))
        self.ubuntu_distros.sort()
        ubuntu_building_config = """\
[ubuntu_building]
architectures: %s
distros: %s
repository_path: /var/repos/ubuntu/building
signing_key: %s
upstream_config: /home/jenkins-agent/reprepro_config
""" % (
            ' '.join(self.architectures),
            ' '.join(self.ubuntu_distros),
            self.gpg_key_id,
        )

        ubuntu_testing_config = """\
[ubuntu_testing]
architectures: %s
distros: %s
repository_path: /var/repos/ubuntu/testing
signing_key: %s
upstream_config: /home/jenkins-agent/reprepro_config
""" % (
            ' '.join(self.architectures),
            ' '.join(self.ubuntu_distros),
            self.gpg_key_id,
        )

        ubuntu_main_config = """\
[ubuntu_main]
architectures: %s
distros: %s
repository_path: /var/repos/ubuntu/main
signing_key: %s
upstream_config: /home/jenkins-agent/reprepro_config
""" % (
            ' '.join(self.architectures),
            ' '.join(self.ubuntu_distros),
            self.gpg_key_id,
        )

        reprepro_config_content = """\
name: ros_bootstrap
method: http://repos.ros.org/repos/ros_bootstrap
suites: [%s]
component: main
architectures: [%s]
verify_release: blindtrust
""" % (
            ', '.join(self.ubuntu_distros),
            ', '.join(self.architectures),
        )

        yaml_str = {
            'master::ip': self.ip_master,
            'repo::ip': self.ip_repo,
            'timezone': SingleQuotedScalarString(self.timezone),
            'ssh_keys': {
                SingleQuotedScalarString(self.ssh_name): {
                    'key': SingleQuotedScalarString(self.ssh_public),
                    'type': self.ssh_type,
                    'user': 'jenkins-agent',
                    'require': SingleQuotedScalarString('User[jenkins-agent]'),
                }
            },
            'jenkins::slave::ui_user': self.jenkins_user,
            'jenkins::slave::ui_pass': SingleQuotedScalarString(self.jenkins_password),
            'user::admin::name': self.jenkins_user,
            'user::admin::password_hash': '#jbcrypt:'
            + PreservedScalarString(
                hashpw(
                    self.jenkins_password.encode('UTF-8'), gensalt(10, prefix=b"2a")
                ).decode('UTF-8')
            ),
            'jenkins::private_ssh_key': PreservedScalarString(self.ssh_private),
            'ssh_host_keys': {'repo': SingleQuotedScalarString(self.repo_hostkey)},
            'jenkins-agent::gpg_key_id': self.gpg_key_id,
            'jenkins-agent::gpg_private_key': PreservedScalarString(
                self.gpg_private_key
            ),
            'jenkins-agent::gpg_public_key': PreservedScalarString(self.gpg_public_key),
            'jenkins-agent::reprepro_updater_config': ubuntu_building_config
            + "\n"
            + ubuntu_testing_config
            + "\n"
            + ubuntu_main_config,
            'jenkins-agent::reprepro_config': {
                SingleQuotedScalarString(
                    '/home/jenkins-agent/reprepro_config/ros_bootstrap.yaml'
                ): {
                    'ensure': SingleQuotedScalarString('present'),
                    'content': PreservedScalarString(reprepro_config_content),
                }
            },
        }
        # If there was an additional hotkey defined, add it to the configuration
        if self.git_fetch_hostkey:
            yaml_str['ssh_host_keys'] = {
                'ssh_host_keys': {
                    'repo': SingleQuotedScalarString(self.repo_hostkey),
                    self.git_fetch_hostkey.split()[0]: SingleQuotedScalarString(
                        self.git_fetch_hostkey
                    ),
                }
            }
        return yaml_str

    def dump_to_disk(self):
        yaml_str = self.to_yaml()
        with open(r'deploy_wizard_configuration.yml', 'w') as yaml_file:
            yaml = YAML()
            yaml.preserve_quotes = True
            yaml.dump(yaml_str, yaml_file)

        if not os.path.exists(os.path.dirname(self.config_filename)):
            os.makedirs(os.path.dirname(self.config_filename))
        with open(self.config_filename, "w") as f:
            f.write(str(self.__dict__))

    def apply_config(self, buildfarm_config_root_folder):
        custom_yaml_config = self.to_yaml()
        yaml = YAML()
        yaml.preserve_quotes = True
        buildfarm_config_files = [
            Path("hiera/hieradata/common.yaml"),
            Path("hiera/hieradata/buildfarm_role/repo.yaml"),
            Path("hiera/hieradata/buildfarm_role/agent.yaml"),
            Path("hiera/hieradata/buildfarm_role/master.yaml"),
        ]

        for buildfarm_config_file in buildfarm_config_files:
            print('Loading file %s' % buildfarm_config_file)
            with open(
                str(buildfarm_config_root_folder / buildfarm_config_file), 'r'
            ) as bcfile:
                hiera_yaml = yaml.load(bcfile)

                for hiera_key in hiera_yaml.keys():
                    if hiera_key in custom_yaml_config.keys():
                        print(
                            'Substituting field %s in file %s'
                            % (hiera_key, str(buildfarm_config_file))
                        )
                        hiera_yaml[hiera_key] = custom_yaml_config[hiera_key]

            with open(
                str(buildfarm_config_root_folder / buildfarm_config_file), 'w'
            ) as bcfile:
                yaml.dump(hiera_yaml, bcfile)

        # The fields credentials::git-fetch-ssh::XXX are not in the original yaml configuration, so they need to be added separately
        # FIXME: here we are adding the raw passphrase, but it should be the hash instead
        if self.git_fetch_ssh_private_key:
            yaml_str = {
                'credentials::git-fetch-ssh::username': SingleQuotedScalarString(
                    self.git_fetch_ssh_username
                ),
                'credentials::git-fetch-ssh::id': self.git_fetch_ssh_id,
                'credentials::git-fetch-ssh::passphrase': SingleQuotedScalarString(
                    self.git_fetch_ssh_passphrase
                ),
                'credentials::git-fetch-ssh::private_key': PreservedScalarString(
                    self.git_fetch_ssh_private_key
                ),
            }
            with open(
                str(
                    buildfarm_config_root_folder
                    / Path("hiera/hieradata/buildfarm_role/master.yaml")
                ),
                'r',
            ) as master_file:
                master_yaml = yaml.load(master_file)
            # Add the new keys (update)
            master_yaml.update(yaml_str)
            with open(
                str(
                    buildfarm_config_root_folder
                    / Path("hiera/hieradata/buildfarm_role/master.yaml")
                ),
                'w',
            ) as master_file:
                yaml.dump(master_yaml, master_file)

    def to_form(self, config):
        form = SummaryForm(
            ssh_name=self.ssh_name,
            ssh_private=self.ssh_private,
            ssh_public=self.ssh_public,
            ssh_type=self.ssh_type,
            git_fetch_ssh_username=self.git_fetch_ssh_username,
            git_fetch_ssh_id=self.git_fetch_ssh_id,
            git_fetch_ssh_passphrase=self.git_fetch_ssh_passphrase,
            git_fetch_ssh_private_key=self.git_fetch_ssh_private_key,
            git_fetch_hostkey=self.git_fetch_hostkey,
            ip_master=self.ip_master,
            ip_repo=self.ip_repo,
            timezone=self.timezone,
            jenkins_user=self.jenkins_user,
            jenkins_password=self.jenkins_password,
            repo_hostkey=self.repo_hostkey,
            gpg_key_id=self.gpg_key_id,
            gpg_private_key=self.gpg_private_key,
            gpg_public_key=self.gpg_public_key,
            custom_repo_url=config['CUSTOM_REPO_URL'],
            git_username=config['GIT_USERNAME'],
            git_passwd=config['GIT_PASSWD'],
            custom_branch=config['CUSTOM_BRANCH'],
        )
        return form
