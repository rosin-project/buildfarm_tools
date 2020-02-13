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

# Import necessary functions from Jinja2 module
from jinja2 import Environment, FileSystemLoader
from ruamel.yaml import YAML
from git import Repo
import tempfile
from pathlib import Path

# Load data from YAML into Python dictionary
yaml = YAML()
with open('vagrant_configuration.yml', 'r') as input_cfg:
    config_data = yaml.load(input_cfg)

# Retrieve the slave's password from the buildfarm_deployment_config repository
buildfarm_config_root_folder = tempfile.mkdtemp()
print(
    "Cloning:\n url={}\n dir={}".format(
        config_data['buildfarm_deployment_config']['git_url'],
        buildfarm_config_root_folder,
    )
)
git_repo = Repo.clone_from(
    config_data['buildfarm_deployment_config']['git_url'],
    buildfarm_config_root_folder,
    branch=config_data['buildfarm_deployment_config']['branch'],
)
print("Repository cloned")
buildfarm_config_common = (
    Path(buildfarm_config_root_folder) / r'hiera/hieradata/common.yaml'
)
with buildfarm_config_common.open() as bfcommon:
    bfcommon_yaml = yaml.load(bfcommon)
    config_data['jenkins_slave_ui_user'] = bfcommon_yaml['jenkins::slave::ui_user']
    config_data['jenkins_slave_ui_pass'] = bfcommon_yaml['jenkins::slave::ui_pass']
    config_data['jenkins_slave_masterurl'] = bfcommon_yaml['jenkins::slave::masterurl']

# Load Jinja2 template
env = Environment(
    loader=FileSystemLoader('./templates'), trim_blocks=True, lstrip_blocks=True
)

print("Generating Vagrantfile...")
vagrant_template = env.get_template('Vagrantfile')
vagrantfile_generated = vagrant_template.render(config_data)
with open('Vagrantfile', 'w') as out_file:
    out_file.write(vagrantfile_generated)

print("Vagrantfile created")

print("Generating config_job.sh file...")
jobs_template = env.get_template('config_jobs.sh')
jobs_generated = jobs_template.render(config_data)
with open('config_jobs.sh', 'w') as out_file:
    out_file.write(jobs_generated)
print("config_job.sh file created")

print("All done!")
