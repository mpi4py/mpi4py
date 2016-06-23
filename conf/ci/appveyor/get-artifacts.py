#!/usr/bin/env python
# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com

import os
import requests

APIURL  = 'https://ci.appveyor.com/api'
ACCOUNT = 'mpi4py/mpi4py'
BRANCH  = 'master'
BRANCH  = 'maint'

branch_url = APIURL + '/projects/' + ACCOUNT + "/branch/" + BRANCH
branch = requests.get(branch_url).json()
jobs = branch['build']['jobs']
jobids = [job['jobId'] for job in jobs]

for jobid in jobids:
    artifacts_url = APIURL + '/buildjobs/' + jobid + '/artifacts'
    artifacts = requests.get(artifacts_url).json()
    filenames = [a['fileName'] for a in artifacts]
    for filename in filenames:
        download_url = artifacts_url + '/' + filename
        print("GET " + download_url)
        continue
        data = requests.get(download_url).content
        with open(os.path.basename(filename), "wb") as f:
            f.write(data)
