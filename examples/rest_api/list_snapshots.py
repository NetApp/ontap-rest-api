#! /usr/bin/env python3

"""
ONTAP REST API Sample Scripts

This script was developed by NetApp to help demonstrate NetApp
technologies.  This script is not officially supported as a
standard NetApp product.

Purpose: Script to list all the snapshots in a cluster using ONTAP REST API.

Usage: python3 list_snapshots.py [-h] -c CLUSTER -v VOLUME_NAME -vs SVM_NAME [-u API_USER]
                         [-p API_PASS]

Copyright (c) 2020 NetApp, Inc. All Rights Reserved.
Licensed under the BSD 3-Clause “New” or Revised” License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause

"""

import base64
import argparse
from getpass import getpass
import logging
import texttable as tt
import requests
import urllib3 as ur
ur.disable_warnings()


def list_snaps(
        cluster: str,
        volume_name: str,
        svm_name: str,
        headers_inc: str):
    """ List Snaps """
    key = get_key(cluster, volume_name, svm_name, headers_inc)
    url4 = "https://{}/api/storage/volumes/{}/snapshots".format(cluster, key)
    response = requests.get(url4, headers=headers_inc, verify=False)
    return response.json()


def get_key(cluster: str, volume_name: str, svm_name: str, headers_inc: str):
    """ Get volume key"""
    tmp = dict(get_volumes(cluster, svm_name, headers_inc))
    vols = tmp['records']
    for i in vols:
        if i['name'] == volume_name:
            return i['uuid']
    return None


def get_volumes(cluster: str, svm_name: str, headers_inc: str):
    """ Get Volumes"""
    url = "https://{}/api/storage/volumes?svm.name={}".format(
        cluster, svm_name)
    response = requests.get(url, headers=headers_inc, verify=False)
    return response.json()


def disp_snaps(
        cluster: str,
        volume_name: str,
        svm_name: str,
        headers_inc: str):
    """Display module for snapshots"""
    tmp = dict(
        list_snaps(
            cluster,
            volume_name,
            svm_name,
            headers_inc))
    snaps = tmp['records']
    tab = tt.Texttable()
    header = ['Snapshot name']
    tab.header(header)
    tab.set_cols_align(['c'])

    for snaplist in snaps:
        sslist = snaplist['name']
        row = [sslist]
        tab.add_row(row)
        tab.set_cols_align(['c'])
    detailtable = tab.draw()
    print(detailtable)


def parse_args() -> argparse.Namespace:
    """Parse the command line arguments from the user"""

    parser = argparse.ArgumentParser(
        description="This script will list snapshots in given ONTAP volume")
    parser.add_argument(
        "-c", "--cluster", required=True, help="API server IP:port details")
    parser.add_argument(
        "-v",
        "--volume_name",
        required=True,
        help="Volume from which snapshot need to be listed.")
    parser.add_argument(
        "-vs",
        "--svm_name",
        required=True,
        help="SVM name from which snapshot need to be listed.")
    parser.add_argument(
        "-u",
        "--api_user",
        default="admin",
        help="API Username")
    parser.add_argument("-p", "--api_pass", help="API Password")
    parsed_args = parser.parse_args()

    # collect the password without echo if not already provided
    if not parsed_args.api_pass:
        parsed_args.api_pass = getpass()

    return parsed_args


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)5s] [%(module)s:%(lineno)s] %(message)s",
    )
    ARGS = parse_args()
    BASE64STRING = base64.encodebytes(
        ('%s:%s' %
         (ARGS.api_user, ARGS.api_pass)).encode()).decode().replace('\n', '')

    headers = {
        'authorization': "Basic %s" % BASE64STRING,
        'content-type': "application/json",
        'accept': "application/json"
    }

    disp_snaps(
        ARGS.cluster,
        ARGS.volume_name,
        ARGS.svm_name,
        headers)
