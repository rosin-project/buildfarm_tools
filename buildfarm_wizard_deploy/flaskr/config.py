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

import logging
import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '94ea769acf4ef77c915b255d99a19b95'
    TESTING = os.environ.get('TESTING')
    BUILDFARM_REPO_URL = (
        'https://github.com/ros-infrastructure/buildfarm_deployment_config.git'
    )
    logging.basicConfig(level=logging.INFO)
