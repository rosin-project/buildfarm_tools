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
from ruamel.yaml.scalarstring import PreservedScalarString as pss
from ruamel.yaml.scalarstring import SingleQuotedScalarString

yaml = YAML()
yaml.preserve_quotes = True
with open(
    r'/root/buildfarm_deployment_config/hiera/hieradata/common.yaml', 'r'
) as yfile:
    config = yaml.load(yfile)

config['master::ip'] = '192.168.50.10'
config['repo::ip'] = '192.168.50.11'

with open(
    r'/root/buildfarm_deployment_config/hiera/hieradata/common.yaml', 'w'
) as yfile:
    yaml.dump(config, yfile)
