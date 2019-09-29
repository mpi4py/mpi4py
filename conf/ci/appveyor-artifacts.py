#!/usr/bin/env python
# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com

import os
import argparse
import requests

APIURL  = 'https://ci.appveyor.com/api'
ACCOUNT = 'mpi4py/mpi4py'
BRANCH  = 'maint'

parser = argparse.ArgumentParser(prog=os.path.basename(__file__))
parser.add_argument("-q", "--quiet", action="store_false",
                    dest="verbose", default=True)
parser.add_argument("-n", "--dry-run", action="store_false",
                    dest="download", default=True)
parser.add_argument("-a", "--account",  type=str, action="store",
                    dest="account", default=ACCOUNT)
parser.add_argument("-b", "--branch",  type=str, action="store",
                    dest="branch", default=BRANCH)
options = parser.parse_args()

ACCOUNT = options.account
BRANCH  = options.branch

branch_url = APIURL + '/projects/' + ACCOUNT + "/branch/" + BRANCH
branch = requests.get(branch_url).json()
jobs = branch['build']['jobs']
jobids = [job['jobId'] for job in jobs]

if options.verbose:
    print("Downloading AppVeyor artifacts "
          "account={} branch={}".format(ACCOUNT, BRANCH))
for jobid in jobids:
    artifacts_url = APIURL + '/buildjobs/' + jobid + '/artifacts'
    artifacts = requests.get(artifacts_url).json()
    filenames = [a['fileName'] for a in artifacts]
    for filename in filenames:
        download_url = artifacts_url + '/' + filename
        if options.verbose:
            print(download_url)
        if options.download:
            data = requests.get(download_url).content
            with open(os.path.basename(filename), "wb") as f:
                f.write(data)
