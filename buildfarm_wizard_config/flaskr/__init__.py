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

from flask import Flask
from flaskr.config import Config
from flaskr.models import BuildFarmConfigData
from flask_bootstrap import Bootstrap
import os

app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)

app.buildfarm_config_data = BuildFarmConfigData()

if app.testing:
    print("Testing mode: {}".format(app.testing))
    # recovering default parameters
    cfg_filename = os.path.dirname(os.path.abspath(__file__))
    cfg_filename += '/../config_wizard_configuration.cfg.test'
    app.buildfarm_config_data.load_complete_config(cfg_filename)

from flaskr import routes
