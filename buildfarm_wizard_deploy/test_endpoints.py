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

from os import environ

environ['TESTING'] = 'True'

from flaskr import app
from flask import url_for
import unittest


class FlaskEndpointTest(unittest.TestCase):
    def setUp(self):
        """Set up test application client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_home_status_code(self):
        """Assert that user successfully lands on homepage"""
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)

    def test_summary_status_code(self):
        result = self.app.get('/summary')
        self.assertEqual(result.status_code, 200)


if __name__ == '__main__':
    unittest.main()
