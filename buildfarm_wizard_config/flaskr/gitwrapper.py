#!/usr/bin/python3
import datetime
from git import Repo, GitCommandError
import os
import shutil
from distutils.dir_util import copy_tree


class GitWrapper(object):
    def __init__(self):
        self.repo_url = ''
        self.content_dir = ''
        self.local_repo = ''
        self.git_repo = None
        self.branch_name = ''

    def clone(self, url, branch_name, local_dir):
        print("Cloning:\n url={}\n dir={}".format(url, local_dir))

        try:
            self.git_repo = Repo.clone_from(url, local_dir)
            self.git_repo.git.fetch()
        except GitCommandError as err:
            print("Error while cloning repository: {} ".format(err))
            return False

        all_branch = []
        origin = self.git_repo.create_remote('custom', url)
        origin.fetch()

        for item in origin.refs:
            all_branch.append(item.name.split('/')[1])

        print("Found branches: {}".format(all_branch))

        head = self.git_repo.create_head(branch_name)
        self.git_repo.head.reference = head

        if branch_name in all_branch:
            self.git_repo.git.pull('origin', branch_name)

        print("Clone created: ")
        print(self.git_repo)

        self.repo_url = url
        self.local_repo = local_dir
        self.branch_name = branch_name
        return True

    def deploy_content(self, folder_path, commit_text="update content"):

        self.content_dir = folder_path
        self.remove_all_files()
        self.copy_all_files()
        self.commit_changes(commit_text)
        return True

    def remove_all_files(self):
        self.current_material = os.listdir(self.local_repo)
        print("removing all files")
        print("Current content: \n{}".format(self.current_material))
        for item in self.current_material:
            if item == ".git":
                continue
            abs_name = self.local_repo + "/" + item
            if os.path.isfile(abs_name):
                print("Removing file {}".format(abs_name))

                self.git_repo.index.remove([abs_name], working_tree=True)
            if os.path.isdir(abs_name):
                print("Removing directory {}".format(abs_name))

                self.git_repo.index.remove([abs_name], working_tree=True, r=True)

        return True

    def copy_all_files(self):
        print("Copying {} into {}".format(self.content_dir, self.local_repo))
        copy_tree(self.content_dir, self.local_repo)

    def commit_changes(self, commit_text):
        print("Comitting changes")
        print("{}".format(self.content_dir))
        generated_material = os.listdir(self.content_dir)

        for item in generated_material:
            print("Handling item {}".format(item))

            spath = self.local_repo + "/" + item
            print("Handling {}".format(spath))
            self.git_repo.index.add([spath])

        # todo set a better commit name.
        self.git_repo.index.commit(commit_text)
        origin = self.git_repo.remote(name='origin')
        origin.push(self.branch_name)
