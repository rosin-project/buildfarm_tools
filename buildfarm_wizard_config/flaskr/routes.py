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

from flask import render_template, redirect, url_for, flash, request
from flaskr import app
from flaskr.forms import InputForm, SelectAddonTag
import os

@app.route('/')
@app.route('/index')
def index():
    return render_template('intro.html')


@app.route('/info_custom_packages', methods=['GET', 'POST'])
def info_custom_packages():
    return render_template('info_custom_packages.html')


@app.route('/info_rosdistro', methods=['GET', 'POST'])
def info_rosdistro():
    return render_template('info_rosdistro.html')


@app.route('/info_rosdistro_addon', methods=['GET', 'POST'])
def info_rosdistro_addon():
    return render_template('info_rosdistro_addon.html')


@app.route('/step_input', methods=['GET', 'POST'])
def step_input():
    form = InputForm()

    if form.validate_on_submit():
        is_ok = app.buildfarm_config_data.load_build_config(form.file_config.data)
        if not is_ok:
            flash('Invalid buildfarm config file!')
            return render_template('step_input.html', form=form)
        app.buildfarm_config_data.distro_model = form.distro_mode.data
        app.buildfarm_config_data.email_buildfarm = form.email.data
        app.buildfarm_config_data.rosdistro_index_url = form.distro_repo.data
        app.buildfarm_config_data.config_repo = form.config_repo.data
        app.buildfarm_config_data.config_branch = form.config_branch.data
        app.config['git_username'] = form.git_username.data
        app.config['git_password'] = form.git_password.data

        if app.buildfarm_config_data.distro_model in ['addon_frozen', 'addon_rosdep']:
            return redirect(url_for('step_rosdistro_addon'))
        return redirect(url_for('step_config_generation_info'))
    else:
        print("Here we are...")
    return render_template('step_input.html', form=form)


@app.route('/step_rosdistro_addon', methods=['GET', 'POST'])
def step_rosdistro_addon():
    form = SelectAddonTag()
    if form.validate_on_submit():
        print(form.selected_tag.data)
        app.buildfarm_config_data.addon_tag = form.selected_tag.data
        return redirect(url_for('step_config_generation_info'))
    return render_template('step_rosdistro_addon.html', form=form)


@app.route('/step_config_generation_info', methods=['GET', 'POST'])
def step_config_generation_info():
    success = True
    success = app.buildfarm_config_data.store()
    return render_template('step_config_generation_info.html',
                           filename=app.buildfarm_config_data.config_filename,
                           success=success)


@app.route('/step_gen_files', methods=['GET', 'POST'])
def step_gen_files():
    success = True
    success = app.buildfarm_config_data.generate_files()

    return render_template('step_gen_files.html',
                           folder=app.buildfarm_config_data.folder_generated,
                           success=success)


@app.route('/step_update_repo', methods=['GET', 'POST'])
def step_update_repo():
    success = True
    success = app.buildfarm_config_data.update_repo(
        app.config['git_username'],
        app.config['git_password'])

    return render_template('step_update_repo.html',
                           config_repo=app.buildfarm_config_data.config_repo,
                           success=success)


@app.route('/step_configure_master', methods=['GET', 'POST'])
def step_configure_master():
    print("Loading step_configure_master")
    url_raw = app.buildfarm_config_data.get_config_repo_raw()
    success = url_raw is not None
    return render_template('step_configure_master.html',
                           config=app.buildfarm_config_data,
                           url_raw=url_raw,
                           success=success)


@app.route('/step_debug', methods=['GET', 'POST'])
def step_debug():
    print("Loading default config")
    cfg_filename = os.path.dirname(os.path.abspath(__file__))
    cfg_filename += '/../config_wizard_configuration.cfg.test'
    is_ok = app.buildfarm_config_data.load_complete_config(cfg_filename)

    return render_template('step_debug.html', success=is_ok)


@app.route('/step_buildfarm_trigger', methods=['GET', 'POST'])
def step_buildfarm_trigger():
    return render_template('step_buildfarm_trigger.html',
                           config=app.buildfarm_config_data)
