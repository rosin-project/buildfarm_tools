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

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    TextAreaField,
    SelectMultipleField,
)
from wtforms.validators import DataRequired, IPAddress, EqualTo, ValidationError
from wtforms.widgets import ListWidget, CheckboxInput
from urllib.parse import urlparse


class SSHForm(FlaskForm):
    ssh_name = StringField(
        'Give a user-friendly name to the SSH key',
        validators=[DataRequired()],
        default="jenkins@buildfarm",
    )
    ssh_private = TextAreaField(
        'SSH Private Key',
        validators=[DataRequired()],
        render_kw={"cols": "60", "rows": "10"},
    )
    ssh_public = TextAreaField(
        'SSH Public Key',
        validators=[DataRequired()],
        render_kw={"cols": "10", "rows": "5"},
    )
    ssh_type = StringField(
        'SSH Key Type', validators=[DataRequired()], default="ssh-rsa"
    )
    submit = SubmitField('Next')

    def validate_ssh_public(form, field):
        if ' ' in field.data:
            raise ValidationError(
                "Public key cannot contain whitespaces; make sure you are not including the key type"
            )


class GitFetchAuthForm(FlaskForm):
    git_fetch_ssh_username = StringField(
        'Username of the SSH key', validators=[DataRequired()]
    )
    git_fetch_ssh_id = StringField(
        'ID of the SSH key (recommended value)',
        validators=[DataRequired()],
        default="2b5cff78-8834-41ab-ac2d-120278815c0e",
    )
    git_fetch_ssh_passphrase = PasswordField('Private SSH key passphrase')
    git_fetch_ssh_private_key = TextAreaField(
        'SSH Private Key',
        validators=[DataRequired()],
        render_kw={"cols": "60", "rows": "10"},
    )
    git_fetch_hostkey = StringField(
        'Hostkey of the git server', validators=[DataRequired()]
    )
    submit = SubmitField('Next')


class IPsAndTimezonesForm(FlaskForm):
    ip_master = StringField('IP address of the master host', validators=[IPAddress()])
    ip_repo = StringField('IP address of the repo host', validators=[IPAddress()])
    timezone = StringField(
        'Timezone', validators=[DataRequired()], default="Europe/Madrid"
    )
    submit = SubmitField('Next')


class JenkinsUserForm(FlaskForm):
    jenkins_user = StringField(
        'Jenkins UI username', validators=[DataRequired()], default="admin"
    )
    jenkins_password = PasswordField(
        'Jenkins UI password', validators=[DataRequired()], default="changeme"
    )
    submit = SubmitField('Next')


class SSHHostkeysForm(FlaskForm):
    repo_hostkey = StringField('Repo\'s hostkey', validators=[DataRequired()])
    submit = SubmitField('Next')


class GPGKeyForm(FlaskForm):
    gpg_key_id = StringField('GPG Key identifier', validators=[DataRequired()])
    gpg_private_key = TextAreaField(
        'GPG private key',
        validators=[DataRequired()],
        render_kw={"cols": "40", "rows": "10"},
    )
    gpg_public_key = TextAreaField(
        'GPG public key',
        validators=[DataRequired()],
        render_kw={"cols": "40", "rows": "10"},
    )
    submit = SubmitField('Next')


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class RepoForm(FlaskForm):
    architectures = ['amd64', 'arm64', 'armhf', 'i386', 'source']
    selected_arch = MultiCheckboxField(
        'Architectures',
        choices=[(arch, arch) for arch in architectures],
        validators=[DataRequired('Select at least one valid architecture')],
    )

    from rosdistro import get_distribution_file, get_index, get_index_url

    index = get_index(get_index_url())
    ros_distributions = index.distributions.keys()
    distributions_combo_list = list()
    list_index = 0
    for item in ros_distributions:
        distribution_file = get_distribution_file(index, item)
        for ubuntu in distribution_file.release_platforms['ubuntu']:
            distributions_combo_list.append(
                (list_index, dict({'ros': item, 'ubuntu': ubuntu}))
            )
            list_index += 1
    distributions_combo_list = sorted(
        distributions_combo_list, key=lambda v: v[1]['ros']
    )
    selected_distros = MultiCheckboxField(
        'Distributions',
        choices=[
            (str(dist[0]), dist[1]['ros'] + ' - ' + dist[1]['ubuntu'])
            for dist in distributions_combo_list
        ],
        validators=[DataRequired('Select at least one valid distribution')],
    )
    submit = SubmitField('Next')


class GitDstForm(FlaskForm):
    custom_repo_url = StringField('Git http URL', validators=[DataRequired()])
    git_username = StringField('Git username', validators=[DataRequired()])
    git_password = PasswordField('Git password', validators=[DataRequired()])
    custom_branch = StringField(
        'Git branch name', validators=[DataRequired()], default="custom-config"
    )
    submit = SubmitField('Next')

    def validate_custom_repo_url(form, field):
        if not urlparse(field.data).scheme in ['http', 'https']:
            raise ValidationError(
                "Currently only http or https git repositories are supported"
            )


class SummaryForm(
    SSHForm,
    GitFetchAuthForm,
    IPsAndTimezonesForm,
    JenkinsUserForm,
    SSHHostkeysForm,
    GPGKeyForm,
    GitDstForm,
):
    submit = SubmitField('Validate configuration and generate (this can take a while)')
