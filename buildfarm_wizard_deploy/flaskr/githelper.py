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

from git import Repo
import datetime
import tempfile
from urllib.parse import urlparse, quote


class GitHelper:
    def __init__(self):
        self.repo_url = ''
        self.local_path = ''
        self.git_repo = None

    def clone(self, url, local_dir=None):
        if local_dir is None:
            local_dir = tempfile.mkdtemp()

        print("Cloning:\n url={}\n dir={}".format(url, local_dir))
        self.git_repo = Repo.clone_from(url, local_dir)

        print("Repository cloned")
        print(self.git_repo)

        self.repo_url = url
        self.local_path = local_dir
        return True

    def push_custom_config(
        self, custom_repo_url, custom_branch_name, git_username, git_passwd
    ):
        url_parsed = urlparse(custom_repo_url)
        auth_custom_repo_url = (
            url_parsed.scheme
            + "://"
            + quote(git_username)
            + ':'
            + quote(git_passwd)
            + '@'
            + url_parsed.netloc
            + url_parsed.path
        )
        custom_remote = self.git_repo.create_remote('custom', auth_custom_repo_url)
        custom_remote.fetch()
        # if the branch already exists in the remote, we generate a new random branch name to avoid conflicts
        custom_branch_name = self.find_branch_in_remote(
            custom_remote, custom_branch_name
        )
        custom_branch = self.git_repo.create_head(custom_branch_name)
        self.git_repo.head.reference = custom_branch

        changedFiles = [item.a_path for item in self.git_repo.index.diff(None)]
        self.git_repo.index.add(changedFiles)
        self.git_repo.index.commit('Add custom configuration by wizard')
        custom_remote.push(custom_branch_name)
        return custom_branch_name

    def find_branch_in_remote(self, custom_remote, custom_branch_name):
        """Looks into the remote to check if there is already a branch with the same name
        If that is the case, to avoid conflicts with changed files, it generates a new random branch name

        Arguments:
            custom_remote:  GitPython remote: should have been previously fetched
            custom_branch_name (str): -- Desired branch name

        Returns:
            str: Free branch name found
        """
        import random

        random.seed()
        free_branch_name = custom_branch_name
        while self.branch_exists(custom_remote, free_branch_name):
            # branch is already used, generate a random new one
            free_branch_name = custom_branch_name + '-' + str(random.randrange(100))
        return free_branch_name

    def branch_exists(self, custom_remote, custom_branch_name):
        for branch in custom_remote.refs:
            # comes in the format 'custom_remote/branch_name'
            remote_branch = branch.name.split('/')[1]
            if remote_branch == custom_branch_name:
                return True
        return False
