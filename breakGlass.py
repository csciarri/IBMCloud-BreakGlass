#!/usr/bin/env python3
##
## This is a Python script that will power off all VSIs and BareMetal servers in an IBM Cloud account. An API Key with the appropriate permissions on the account is required
## Currently supports: Classic VSIs, Classic BareMetal
##
## License: MIT License 
## Author: Chris Sciarrino
## Version: 0.1
## Email: sciar@ca.ibm.com
##

import SoftLayer, sys

#Function to put welcome message
def start():
    print("*****************************************************************************************************************************")
    print("*         This script is meant to be used in a situation where ALL VSIs must be powered off quickly. Use with CAUTION.         *")
    print("*****************************************************************************************************************************\n")


#Function to get classic API key from user and confirm that they want to proceed
def getClassicCreds():
    username = input("Enter Classic API Username: ")
    api_key = input("Enter Classic API Key: ")
    
    confirmation = input("\nTHIS WILL POWER OFF ALL IBM CLOUD CLASSIC VSIs and BareMetal, ARE YOU SURE YOU WANT TO PROCEED? (Y/N):\n").upper()
    
    if confirmation == "N":
        print("Exiting\n")
        sys.exit()
    elif confirmation == "Y":
        return (username, api_key)


#Use Classic API Key to get a list of VSIs in the account
def getClassicVSI(username, api_key):
    client = SoftLayer.create_client_from_env(username=username, api_key=api_key) 
    vsi_list = (client.call('SoftLayer_Account', 'getVirtualGuests',mask='powerState'))
    return vsi_list


#Use the list of VSIs to issue poweroff API command for VSIs that are powered on.  
def powerOffClassic(vsi_list, username, api_key):
    client = SoftLayer.create_client_from_env(username=username, api_key=api_key) 
    POWERED_ON_VM_IDS = []
    for vsi in vsi_list:
        for key, value in vsi.items():
            if key == 'fullyQualifiedDomainName':
                VM_NAME = value
            if key == 'id':
                VM_ID = value
            if key == 'powerState':
                for x, y in value.items():
                    if x == 'keyName':
                        VM_POWER_STATE = y
        try:
                print("\n------------------------------------------------------------------------------------------------------------------------------------------------")
                print("VSI NAME: " + VM_NAME + "\nVSI ID: " + str(VM_ID) + "\nPower State: " + VM_POWER_STATE +"\n")

                if VM_POWER_STATE == 'RUNNING':
                    POWERED_ON_VM_IDS.append(VM_ID)
                    print("Attempting to power off VM...\n")
                    client.call('SoftLayer_Virtual_Guest', 'powerOff', id=VM_ID)
                    print("Done.")
        except:
            print("Error occured with " + VM_NAME)
    return POWERED_ON_VM_IDS

#Use Classic API Key to get a list of BareMetal Servers in the account
def getClassicHardware(username, api_key):
    client = SoftLayer.create_client_from_env(username=username, api_key=api_key) 
    classic_bm_list = (client.call('SoftLayer_Account', 'getHardware'))
    return classic_bm_list


#Use the list of BareMetal servers to issue poweroff API command for BMs that are powered on.  
def powerOffClassicHardware(classic_bm_list, username, api_key):
    client = SoftLayer.create_client_from_env(username=username, api_key=api_key) 
    POWERED_ON_BM_IDS = []
    for servers in classic_bm_list:
        for key, value in servers.items():
            if key == 'fullyQualifiedDomainName':
                BM_NAME = value
            if key == 'id':
                BM_ID = value
                BM_POWER_STATE = (client.call('SoftLayer_Hardware', 'getServerPowerState',id=BM_ID))
        try:
            print("\n------------------------------------------------------------------------------------------------------------------------------------------------")
            print("BareMetal Server NAME: " + BM_NAME + "\nBareMetal Server ID: " + str(BM_ID) + "\nPower State: " + BM_POWER_STATE +"\n")
            if BM_POWER_STATE == 'on':
                    POWERED_ON_BM_IDS.append(BM_ID)
                    print("Attempting to power off BM...\n")
                    client.call('SoftLayer_Hardware', 'powerOff', id=BM_ID)
                    print("Done.\n")
        except:
            print("Error occured with " + BM_NAME)
    return POWERED_ON_BM_IDS
    
def summary(classic_bm_list, vsi_list, POWERED_ON_BM_IDS, POWERED_ON_VM_IDS):
    print("\n------------------------------------------------------------------------------------------------------------------------------------------------")
    print("\nThere were a total of " + str(len(vsi_list)) + " Classic VSIs found and " + str(len(POWERED_ON_VM_IDS)) + " were in the Powered On state")
    print("\nThere were a total of " + str(len(classic_bm_list)) + " Classic BMs found and " + str(len(POWERED_ON_BM_IDS)) + " were in the Powered On state")
    

#Call Functions
start()
(username, api_key) = getClassicCreds()
classic_bm_list = getClassicHardware(username, api_key)
vsi_list = getClassicVSI(username, api_key)
POWERED_ON_VM_IDS = powerOffClassic(vsi_list, username, api_key)
POWERED_ON_BM_IDS = powerOffClassicHardware(classic_bm_list, username, api_key)
summary(classic_bm_list, vsi_list, POWERED_ON_BM_IDS, POWERED_ON_VM_IDS)