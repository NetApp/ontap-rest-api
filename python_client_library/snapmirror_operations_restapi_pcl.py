#! /usr/bin/env python3

"""
ONTAP REST API Python Sample Scripts

This script was developed by NetApp to help demonstrate NetApp technologies. This
script is not officially supported as a standard NetApp product.

Purpose: THE FOLLOWING SCRIPT SHOWS SNAPMIRROR OPERATIONS USING REST API PCL

Usage: volume_operations_restapi_pcl.py -a <Cluster Address> -u <User Name> -p <Password Name>

Copyright (c) 2020 NetApp, Inc. All Rights Reserved.
Licensed under the BSD 3-Clause “New” or Revised” License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause

"""

import argparse
from getpass import getpass
import logging

from netapp_ontap import config,HostConnection, NetAppRestError
from netapp_ontap.resources import Svm, Volume, SnapmirrorRelationship, SnapmirrorTransfer

def show_svm():	
    print()
    print ("Getting SVM Details")
    print ("===================")
    try:
        for svm in Svm.get_collection(fields="uuid"):
            print ("SVM name:-%s ; SVM uuid:-%s " % (svm.name,svm.uuid))
    except NetAppRestError as e:
        print ("HTTP Error Code is " % e.http_err_response.http_response.text)
        print("Exception caught :" + str(e))
    return	
		
def show_volume():	
    print("The List of SVMs")
    print("===================")
    show_svm()
    print()
    svm_name = input("Enter the SVM from which the Volumes need to be listed:-")
    print()
    print ("Getting Volume Details")
    print ("===================")

    try:
        for volume in Volume.get_collection(**{"svm.name": svm_name},fields="uuid"):
             print("Name = %s; UUID = %s" % (volume.name,volume.uuid))               
    except NetAppRestError as e:
        print ("HTTP Error Code is " % e.http_err_response.http_response.text)
        print("Exception caught :" + str(e))
    return
	
def show_snapshot():	
    print()
    print("The List of SVMs:-")
    show_svm()
    print()
    svm_name = input("Enter the SVM from which the Volumes need to be listed:-")
    print()
    show_volume(svm_name)
    print()
    vol_uuid = input("Enter the Volume UUID from which the Snapshots need to be listed [UUID]:-")		
    print ("The List of Snapshots:-")    
    try:
        for snapshot in Snapshot.get_collection(vol_uuid):
            print(snapshot.name)
    except NetAppRestError as e:
        print ("HTTP Error Code is " % e.http_err_response.http_response.text)
        print("Exception caught :" + str(e))				
    return

def show_snapmirror():	
    print("List of SnapMirror Relationships:")
    print("=================================")

    try:
        for snapmirrorrelationship in SnapmirrorRelationship.get_collection(fields="uuid"):
            print(snapmirrorrelationship.uuid)
            snapmirror1 = SnapmirrorRelationship.find(uuid=snapmirrorrelationship.uuid)
            print(snapmirror1.source.path)
            print(snapmirror1.destination.path)
            print(snapmirror1.state)
            print("-----------------------------")
    except NetAppRestError as e:
        print ("HTTP Error Code is " % e.http_err_response.http_response.text)
        print("Exception caught :" + str(e))
    return	
	
def create_snapmirror():
    print ("===================")
    print("Please enter the following details:-")
    src_svm_name = input("Enter the Source SVM :-")
    src_vol_name = input("Enter the Source Volume :-")
    dst_svm_name = input("Enter the Destination SVM :-")
    dst_vol_name = input("Enter the Destination Volume :-")
    
    dataObj = {}
    src = src_svm_name + ":" + src_vol_name
    dst = dst_svm_name + ":" + dst_vol_name
    dataObj['source']={"path": src}
    dataObj['destination']={"path": dst}
	
    snapmirrorrelationship = SnapmirrorRelationship.from_dict(dataObj)
	
    try:
        if(snapmirrorrelationship.post(poll=True)):
            print ("SnapmirrorRelationship  %s created Successfully")
    except NetAppRestError as e:
        print ("HTTP Error Code is " % e.http_err_response.http_response.text)
        print("Exception caught :" + str(e)) 
    return
	
def patch_snapmirror():
    print ("=============================================")
    print()
    show_snapmirror()
	
    snapmirror_uuid = input("Enter the UUID of the snapmirror to be updated:-")
    snapmirrortransfer = SnapmirrorRelationship.find(uuid=snapmirror_uuid)   
    snapchoice = input("What state update would you like? [snapmirrored/paused/broken_off/uninitialized/synchronizing] ")
    snapmirrortransfer.state = snapchoice    
	
    try:	
        if(snapmirrortransfer.patch(poll=True)):
            print ("Snapmirror Relationship   Updated Successfully" )
    except NetAppRestError as e:
        print ("HTTP Error Code is " % e.http_err_response.http_response.text)
        print("Exception caught :" + str(e)) 
    return

def delete_snapmirror():
    print ("=============================================")
    print()
    show_snapmirror()
	
    snapmirror_uuid = input("Enter the UUID of the snapmirror to be deleted:-")
    snapmirrorrelationship = SnapmirrorRelationship.find(uuid=snapmirror_uuid)	
    
    try:
        if(snapmirrorrelationship.delete(poll=True)):
            print ("Snapmirror Relationship    has been deleted Successfully.")
    except NetAppRestError as e:
        print ("HTTP Error Code is " % e.http_err_response.http_response.text)
        print("Exception caught :" + str(e))
    return

  	

def sm_ops():
    print("THE FOLLOWING SCRIPT SHOWS SNAPMIRROR OPERATION USING REST API PYTHON CLIENT LIBRARY")
    print("====================================================================================")
    print()
    snapmirrorbool = input("What state SnapMirror Operation would you like? SnapMirror [show/create/update/delete] ")
    if snapmirrorbool == 'show':
       print("====")
       show_snapmirror()
    if snapmirrorbool == 'create':
       create_snapmirror()
    if snapmirrorbool == 'update':
       patch_snapmirror()
    if snapmirrorbool == 'delete':
       delete_snapmirror()   
    return

	
def parse_args() -> argparse.Namespace:
    """Parse the command line arguments from the user"""

    parser = argparse.ArgumentParser(
        description="THE FOLLOWING SCRIPT SHOWS SNAPMIRROR OPERATIONS USING REST API PYTHON CLIENT LIBRARY:-"
    )
    parser.add_argument(
        "-c", "--cluster", required=True, help="API server IP:port details"
    )
    parser.add_argument("-u", "--api_user", default="admin", help="API Username")
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
    args = parse_args()
    config.CONNECTION = HostConnection(
        args.cluster, username=args.api_user, password=args.api_pass, verify=False,
    )
    sm_ops()

