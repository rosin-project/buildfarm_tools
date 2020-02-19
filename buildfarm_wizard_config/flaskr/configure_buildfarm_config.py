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

import os
import sys
from jinja2 import Environment, FileSystemLoader, exceptions


class Generator(object):

    """Class handling the file generation

    Attributes:
        context (str): Filename containing the requested configuration through yaml file
        path (str): Description
        template_environment (Environment): Jinja2 component (to be clarified)
    """

    def __init__(self, template_path, output_path):
        self.out_path = output_path
        self.template_path = template_path
        self.template_environment = None
        self.context = None

    def generate_all(self, config):
        """Entry point for generating all files (no directory)
        Args:
            config (dict): requested configuration
        """

        if not os.path.isdir(self.out_path):
            os.makedirs(self.out_path)

        self.template_environment = Environment(autoescape=False,
                                                loader=FileSystemLoader(self.template_path),
                                                trim_blocks=True)
        try:
            with open(config, 'r') as open_file:
                dictname = open_file.read()
                self.context = eval(dictname)
        except FileNotFoundError as err:
            print("Could not find file {}".format(err))
            return False

        # check file to generate
        all_items = os.listdir(self.template_path)

        for item in all_items:
            if item == ".git":
                continue
            try:
                self.generate(item, self.out_path + "/" + item)
            except exceptions.TemplateSyntaxError as err:
                print("Error while generating file {}, line {}: {}".format(item, err.lineno, err))
                return False
        return True

    def generate(self, input_file, output_file, config=None):
        """Generate a given file

        Args:
            input_file (str): Template file
            output_file (TYPE): File to be written
            config(dict): context file. If None, use the one stored
        Returns:
            None: Nothing
        """

        print("Generating {}".format(input_file))
        if config:
            print("using provided config")
        else:
            print("Using default config")
        # only if we are considering a file
        file_path = self.template_path + "/" + input_file
        if not os.path.isfile(file_path):
            print("Skipping directory {}".format(input_file))
            return

        if not config:
            file_generated = self.template_environment.get_template(input_file).render(self.context)
        else:
            file_generated = self.template_environment.get_template(input_file).render(config)

        with open(output_file, 'w') as out_file:
            out_file.write(file_generated)

    def generate_distributions(self):
        """Generate the directory related to distributions
        """

        try:
            for item in self.context['ros_distros']:
                print("Handling distribution {}".format(item))

                ubuntu_distros = [item2['ubuntu'] for item2 in self.context['distros'] if item2['ros'] == item]

                print("Associated platform {}".format(ubuntu_distros))

                local_context = self.context.copy()
                local_context['ros_distribution'] = item
                local_context['ubuntu_with_ros'] = ubuntu_distros
                os.makedirs(self.out_path + "/" + item)

                files = os.listdir(self.template_path + "/distributions")

                for onefile in files:
                    input_file = "distributions/" + onefile
                    output_file = self.out_path + "/" + item + "/" + onefile
                    print("generating {}".format(output_file))

                    self.generate(input_file, output_file, local_context)
        except RuntimeError as err:
            print("Error while accessing to ubuntu distribution: {}".format(err))
            return False
        except TypeError as err:
            print("Error while generating files: {}".format(err))
            return False
        except exceptions.TemplateSyntaxError as err:
            print("Error while generating file {}, line {}: {}".format(item, err.lineno, err))
            return False
        return True


USAGE = """ python configure_buildfarm_config.py output_path my_config.yaml
output_path: relative / absolute path where the generated fields are to be placed.
my_config.yaml: path to the file containing all essential configuration information

Example of call:
python configure_buildfarm_config.py /tmp/trial minimum_config.yaml
"""


def main():
    print("Hello, this is buildfarm config generator")

    if len(sys.argv) != 3:
        print("Wrong input parameters")
        print(USAGE)
        return

    generator = Generator("rosdistro_template", sys.argv[1])
    generator.generate_all(sys.argv[2])
    generator.generate_distributions()

    print("Bye")


if __name__ == '__main__':
    main()
