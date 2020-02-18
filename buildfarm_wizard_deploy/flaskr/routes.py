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

from flask import render_template, redirect, url_for
from flaskr import app
from flaskr.forms import (
    SSHForm,
    IPsAndTimezonesForm,
    JenkinsUserForm,
    SSHHostkeysForm,
    GPGKeyForm,
    RepoForm,
    GitDstForm,
    SummaryForm,
    GitFetchAuthForm,
)
from os import path
from flaskr.githelper import GitHelper
import datetime
from bcrypt import hashpw, gensalt
from flask import Markup


@app.route('/')
@app.route('/index')
def index():
    return render_template('intro.html')


@app.route('/step_ssh', methods=['GET', 'POST'])
def step_ssh():
    form = SSHForm()
    if form.validate_on_submit():
        app.buildfarm_data.ssh_name = form.ssh_name.data
        app.buildfarm_data.ssh_type = form.ssh_type.data
        app.buildfarm_data.ssh_private = form.ssh_private.data
        app.buildfarm_data.ssh_public = form.ssh_public.data
        return redirect(url_for('step_ask_priv_repo'))
    return render_template('step_ssh.html', form=form)


@app.route('/step_ask_priv_repo', methods=['GET', 'POST'])
def step_ask_priv_repo():
    return render_template('step_ask_priv_repo.html')


@app.route('/step_request_priv_repo', methods=['GET', 'POST'])
def step_request_priv_repo():
    form = GitFetchAuthForm()
    if form.validate_on_submit():
        app.buildfarm_data.git_fetch_ssh_username = form.git_fetch_ssh_username.data
        app.buildfarm_data.git_fetch_ssh_id = form.git_fetch_ssh_id.data
        app.buildfarm_data.git_fetch_ssh_passphrase = form.git_fetch_ssh_passphrase.data
        app.buildfarm_data.git_fetch_ssh_private_key = (
            form.git_fetch_ssh_private_key.data
        )
        app.buildfarm_data.git_fetch_hostkey = form.git_fetch_hostkey.data
        return redirect(url_for('step_ips'))
    return render_template('step_request_priv_repo.html', form=form)


@app.route('/step_ips', methods=['GET', 'POST'])
def step_ips():
    form = IPsAndTimezonesForm()
    if form.validate_on_submit():
        app.buildfarm_data.ip_master = form.ip_master.data
        app.buildfarm_data.ip_repo = form.ip_repo.data
        app.buildfarm_data.timezone = form.timezone.data
        return redirect(url_for('step_jenkins'))
    return render_template('step_ips.html', form=form)


@app.route('/step_jenkins', methods=['GET', 'POST'])
def step_jenkins():
    form = JenkinsUserForm()
    if form.validate_on_submit():
        app.buildfarm_data.jenkins_user = form.jenkins_user.data
        app.buildfarm_data.jenkins_password = form.jenkins_password.data
        return redirect(url_for('step_hostkeys'))
    return render_template('step_jenkins.html', form=form)


@app.route('/step_hostkeys', methods=['GET', 'POST'])
def step_hostkeys():
    form = SSHHostkeysForm()
    if form.validate_on_submit():
        app.buildfarm_data.repo_hostkey = form.repo_hostkey.data
        return redirect(url_for('step_gpg'))
    return render_template('step_hostkeys.html', form=form)


@app.route('/step_gpg', methods=['GET', 'POST'])
def step_gpg():
    form = GPGKeyForm()
    if form.validate_on_submit():
        app.buildfarm_data.gpg_key_id = form.gpg_key_id.data
        app.buildfarm_data.gpg_private_key = form.gpg_private_key.data
        app.buildfarm_data.gpg_public_key = form.gpg_public_key.data
        return redirect(url_for('step_repo'))
    return render_template('step_gpg.html', form=form)


@app.route('/step_repo', methods=['GET', 'POST'])
def step_repo():
    form = RepoForm()
    if form.validate_on_submit():
        app.buildfarm_data.architectures = form.selected_arch.data
        app.buildfarm_data.distros = [
            x[1]
            for x in form.distributions_combo_list
            if str(x[0]) in form.selected_distros.data
        ]
        return redirect(url_for('git_form'))
    return render_template('step_repo.html', form=form)


@app.route('/git_form', methods=['GET', 'POST'])
def git_form():
    form = GitDstForm()
    if form.validate_on_submit():
        app.config['CUSTOM_REPO_URL'] = form.custom_repo_url.data
        app.config['GIT_USERNAME'] = form.git_username.data
        app.config['GIT_PASSWD'] = form.git_password.data
        app.config['CUSTOM_BRANCH'] = form.custom_branch.data
        return redirect(url_for('summary'))
    return render_template('step_git_info.html', form=form)


@app.route('/summary', methods=['GET', 'POST'])
def summary():
    form = app.buildfarm_data.to_form(app.config)
    # Do not show the password fields, as I cannot "prefill" them
    del form.jenkins_password
    del form.git_password
    del form.git_fetch_ssh_passphrase

    if not app.buildfarm_data.git_fetch_ssh_private_key:
        del form.git_fetch_hostkey
        del form.git_fetch_ssh_id
        del form.git_fetch_ssh_passphrase
        del form.git_fetch_ssh_private_key
        del form.git_fetch_ssh_username

    if form.validate_on_submit():
        app.buildfarm_data.ssh_name = form.ssh_name.data
        app.buildfarm_data.ssh_type = form.ssh_type.data
        app.buildfarm_data.ssh_private = form.ssh_private.data
        app.buildfarm_data.ssh_public = form.ssh_public.data
        if app.buildfarm_data.git_fetch_ssh_private_key:
            app.buildfarm_data.git_fetch_ssh_username = form.git_fetch_ssh_username.data
            app.buildfarm_data.git_fetch_ssh_id = form.git_fetch_ssh_id.data
            app.buildfarm_data.git_fetch_ssh_private_key = (
                form.git_fetch_ssh_private_key.data
            )
            app.buildfarm_data.git_fetch_hostkey = form.git_fetch_hostkey.data
        app.buildfarm_data.ip_master = form.ip_master.data
        app.buildfarm_data.ip_repo = form.ip_repo.data
        app.buildfarm_data.timezone = form.timezone.data
        app.buildfarm_data.jenkins_user = form.jenkins_user.data
        app.buildfarm_data.repo_hostkey = form.repo_hostkey.data
        app.buildfarm_data.gpg_key_id = form.gpg_key_id.data
        app.buildfarm_data.gpg_private_key = form.gpg_private_key.data
        app.buildfarm_data.gpg_public_key = form.gpg_public_key.data
        app.config['CUSTOM_REPO_URL'] = form.custom_repo_url.data
        app.config['GIT_USERNAME'] = form.git_username.data
        app.config['CUSTOM_BRANCH'] = form.custom_branch.data
        return redirect(url_for('generate_config'))
    return render_template('summary.html', buildfarm_data=app.buildfarm_data, form=form)


@app.route('/generate_config', methods=['GET', 'POST'])
def generate_config():
    output_msgs = []
    output_msgs.append('Dumping configuration')
    app.buildfarm_data.dump_to_disk()
    output_msgs.append(
        Markup(
            'All configuration has been stored in the file <mark>{}</mark>'.format(
                app.buildfarm_data.config_filename
            )
        )
    )
    output_msgs.append('Cloning buildfarm')
    git_helper = GitHelper()

    if not git_helper.clone(app.config['BUILDFARM_REPO_URL']):
        output_msgs.append(
            'There was an error cloning the buildfarm_deployment_config repository'
        )
    else:
        output_msgs.append(
            'The repository buildfarm_deployment_config repository has been sucessfully cloned'
        )

    output_msgs.append('Applying custom configuration')
    app.buildfarm_data.apply_config(git_helper.local_path)
    output_msgs.append('Pushing configuration to git repository')
    used_branch_name = git_helper.push_custom_config(
        app.config['CUSTOM_REPO_URL'],
        app.config['CUSTOM_BRANCH'],
        app.config['GIT_USERNAME'],
        app.config['GIT_PASSWD'],
    )
    if not used_branch_name == app.config['CUSTOM_BRANCH']:
        output_msgs.append(
            Markup(
                'The branch <mark>{}</mark> already existed in the git repository; to avoid conflicts, a new branch named <mark>{}</mark> has been created to store the buildfarm configuration. Please, be sure to use the proper branch name to deploy the buildfarm.'.format(
                    app.config['CUSTOM_BRANCH'], used_branch_name
                )
            )
        )
    output_msgs.append('Configuration successfull')

    return render_template(
        'generate_config.html',
        output_msgs=output_msgs,
        cfg_filename=app.buildfarm_data.config_filename,
        git_dst_repo=app.config['CUSTOM_REPO_URL'],
        git_dst_branch=used_branch_name,
    )
