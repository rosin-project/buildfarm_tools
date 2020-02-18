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
from flaskr.models import BuildfarmData
from flask_bootstrap import Bootstrap
import os
from pathlib import Path

app = Flask(__name__)
app.logger.info('Initializing (this can take some time)')
app.config.from_object(Config)
bootstrap = Bootstrap(app)

if app.testing:
    # Load some dummy data here; used for testing
    app.logger.info('Loading test data')
    cfg_filename = Path(app.root_path).parent.joinpath('deploy_wizard_data.cfg.test')
    app.buildfarm_data = BuildfarmData(str(cfg_filename.resolve()))
    cfg_filename = Path(app.root_path).parent.joinpath('deploy_wizard_config.test')
    app.config.from_pyfile(str(cfg_filename.resolve()), silent=False)
else:
    app.buildfarm_data = BuildfarmData()

from flaskr import routes
