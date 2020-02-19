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
from flask_wtf.file import FileRequired, FileAllowed, FileField
from wtforms import (
    StringField,
    SubmitField,
    SelectField,
    SelectMultipleField,
    PasswordField,
)
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import Optional, DataRequired, InputRequired, Email, ValidationError
from urllib.parse import urlparse


class InputForm(FlaskForm):
    file_config = FileField(
        'Deploy Configuration',
        validators=[FileRequired()])
    distro_modes = ['addon_frozen', 'full distro', 'addon_rosdep']

    distro_mode = SelectField(
        'ros distro model',
        choices=[(rosdistro, rosdistro) for rosdistro in distro_modes],
        validators=[DataRequired('Select at least one distribution model')])
    email = StringField(
        'Administrator email',
        validators=[InputRequired("Please enter your email address."),
        Email("This field requires a valid email address")])
    distro_repo = StringField('rosdistro repository',
                              validators=[DataRequired()])

    config_repo = StringField('buildfarm_config fork repository',
                              validators=[DataRequired()])
    git_username = StringField('Git username')
    git_password = PasswordField('Git password')
    config_branch = StringField("Branch name",
                                validators=[DataRequired()],
                                default="wizard-config")
    submit = SubmitField('Next')

    def validate_git_username(form, field):

        url_parsed = urlparse(form.config_repo.data)
        is_credential = url_parsed.scheme in ['http', 'https']

        if is_credential and not field.data:
            raise ValidationError('username required for http and https protocols')

    def validate_git_password(form, field):

        url_parsed = urlparse(form.config_repo.data)
        is_credential = url_parsed.scheme in ['http', 'https']

        if is_credential and not field.data:
            raise ValidationError('password required for http and https protocols')


class SelectAddonTag(FlaskForm):
    selected_tag = StringField('Tag for the addon description',
                               validators=[DataRequired()])
    submit = SubmitField('Ready')
