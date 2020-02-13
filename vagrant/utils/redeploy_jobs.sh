#!/usr/bin/env bash
# Copyright 2019 Tecnalia Research & Innovation
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

vagrant ssh rosin-test-alpha -c "sudo su -c 'cd /root ; bash /vagrant/config_jobs.sh'"
vagrant ssh rosin-test-alpha -c "sudo docker run -d --restart unless-stopped --name buildfarm_config -p 8000:80 -v /root/ros_buildfarm_config:/usr/share/nginx/html:ro nginx:alpine"
vagrant ssh rosin-test-alpha -c "sudo docker run -d --restart unless-stopped --name rosdistro -p 8081:80 -v /root/rosdistro:/usr/share/nginx/html:ro nginx:alpine"
vagrant ssh rosin-test-alpha -c "sudo su -c 'cd /root ; . venv/bin/activate ;  generate_all_jobs.py --commit http://192.168.50.10:8000/index.yaml'"
