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

if [ $# -ne 2 ]; then
    echo "Syntax: $0 git_url branch_name"
    exit
fi

GIT_URL=$1
BRANCH_NAME=$2

vagrant ssh rosin-test-beta -c "sudo rm -rf /root/buildfarm_deployment_config ; sudo git clone ${GIT_URL} --branch ${BRANCH_NAME} /root/buildfarm_deployment_config ; sudo /vagrant/fix_ips.py ; sudo rm -rf /root/buildfarm_deployment ; sudo -s <<< 'cd /root/buildfarm_deployment_config ; ./reconfigure.bash agent'" &

vagrant ssh rosin-test-gamma -c "sudo rm -rf /root/buildfarm_deployment_config ; sudo git clone ${GIT_URL} --branch ${BRANCH_NAME} /root/buildfarm_deployment_config ; sudo /vagrant/fix_ips.py ; sudo rm -rf /root/buildfarm_deployment ; sudo -s <<< 'cd /root/buildfarm_deployment_config ; ./reconfigure.bash repo'" &
