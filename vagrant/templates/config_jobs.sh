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

set -e # To fail on errors

cd ~

# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

apt install -y python3 python3-all python3-pip python3-venv
pyvenv --without-pip venv
. venv/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python3
pip3 install empy
pip3 install jenkinsapi
pip3 install rosdistro
pip3 install catkin_pkg
pip3 install {{ ros_buildfarm.git_url }}@{{ ros_buildfarm.branch }}

mkdir /root/.buildfarm
touch /root/.buildfarm/jenkins.ini
cat > /root/.buildfarm/jenkins.ini << EOF
[{{ jenkins_slave_masterurl }}]
username={{ jenkins_slave_ui_user }}
password={{ jenkins_slave_ui_pass }}
EOF

cd ~

git clone --single-branch -b {{ ros_buildfarm_config.branch }} {{ ros_buildfarm_config.git_url }}
cd ros_buildfarm_config
# Change the hostnames of the yaml files by fixed IP addresses
sed -i 's#\(jenkins_url: \)\(.*\)$*#\1http://master:8080#g' index.yaml
find . -type f -name '*.yaml' -exec sed -i 's#\([:space]*- http://\)\([a-z\.\-]*\)/\([a-zA-Z]*\)/\([a-zA-Z]*\)#\1192.168.50.11/\3/\4#g' {} \;
find . -type f -name '*.yaml' -exec sed -i 's#\(target_repository: http://\)\([a-z\.\-]*\)/\([a-zA-Z]*\)/\([a-zA-Z]*\)#\1192.168.50.11/\3/\4#g' {} \;
find . -type f -name '*.yaml' -exec sed -i 's#\(canonical_base_url: http://\)\([a-z\.\-]*\)/\([a-zA-Z]*\)#\1192.168.50.11/\3#g' {} \;
sed -i 's#^rosdistro_index_url: [[:print:]]*$#rosdistro_index_url: http://192.168.50.10:8081/index.yaml#g' index.yaml
{% if not skip_deploy %}
docker run -d --restart unless-stopped --name buildfarm_config -p 8000:80 -v "$PWD":/usr/share/nginx/html:ro nginx:alpine
{% endif %}

cd ~

git clone --single-branch -b {{ rosdistro.branch }} {{ rosdistro.git_url }}
cd rosdistro/
sed -i 's#\(distribution_cache: http://\)\([a-z\.\-]*\)#\1192.168.50.11#g' index.yaml
{% if not skip_deploy %}
docker run -d --restart unless-stopped --name rosdistro -p 8081:80 -v "$PWD":/usr/share/nginx/html:ro nginx:alpine
{% endif %}

{% if not skip_job_generation and not skip_deploy %}
generate_all_jobs.py --commit http://192.168.50.10:8000/index.yaml
{% endif %}
