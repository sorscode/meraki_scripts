# Generic modules
import json
import os
import sys
import time
import csv

# Meraki specific modules
import merakiapi as m
import requests
from vars import apikey, organizationid

# Global Variables
devicemodel = 'MX' # MR/MS/MX/MV
max = 2640    # 2800+ for all
time_24hr = 86400 # 86400 = 24hr
time_days = 30 # How many days do you want data usage
total_time = time_24hr * time_days
vlan_check = 150 # Specify the VLAN you want Data Usage from

# Global Dictionaries
filtered = []
filterresults = []
networkinfo = []
clientinfo = []

def get_org_inv():
    print('Get Device List')
    # define local variables for the function
    orglist = m.getorginventory(apikey, organizationid, suppressprint=True)
    count = 0
    # Time to get a list of all the networks
    for row in orglist:
        model = row['model']
        if model[:2] == devicemodel: # Filter out only the network types we want to see
            if count < max:
                filterresults.append({'networkId': row['networkId'],'serial': row['serial'], 'model': row['model']})
                count += 1
                print(str(count) + " - " + row['serial'] + " - " + row['networkId'])

def get_network_info():
    print('Getting Network Information')
    for row in filterresults:
        fac_number = m.getnetworkdetail(apikey, row['networkId'], suppressprint=True)
        networkinfo.append({'name': fac_number['name'], 'serial': row['serial'] })
        print(fac_number['name'] + " - " + row['serial'])

def get_client_info():
    print('Get Client list')
    for row in networkinfo:
        data_usage = m.getclients(apikey, row['serial'], timestamp=total_time, suppressprint=True)
        for i in data_usage:
            clientinfo.append(
                {'name': row['name'], \
                'description': i['description'], \
                'mac': i['mac'], \
                'vlan': i['vlan'], \
                'sent': i['usage']['sent'], \
                'recv': i['usage']['recv']})

def print_client_info():
    for row in clientinfo:
        if row['vlan'] is 150:
            print(row['name'] + " - " + str(row['description']) + " - " + row['mac'] + " - " + str(row['vlan']))

def filter_data():
    for row in clientinfo:
        if row['vlan'] is vlan_check:
            filtered.append(
                {'name': row['name'], \
                'description': row['description'], \
                'mac': row['mac'], \
                'vlan': row['vlan'], \
                'sent': row['sent'], \
                'recv': row['recv']}
            )

def output_client_csv():
    timestr = time.strftime("%Y-%m-%d-%H%M%S")
    with open('client_list-' + timestr + '.csv', 'a') as outcsv:
        writer = csv.writer(outcsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerow(['Facility','Description', 'MAC Address', 'Vlan', 'Sent - Kb', 'Received - Kb'])
        for item in filtered:
            if item['description'] is None:
                writer.writerow([item['name'], 'No Description', item['mac'], item['vlan'], item['sent'], item['recv']])
            else:
                writer.writerow([item['name'], item['description'], item['mac'], item['vlan'], item['sent'], item['recv']])

def main():
    # List all the functions we want to run in the order we want them to run
    get_org_inv()
    get_network_info()
    get_client_info()
    #print_client_info()
    filter_data()
    #print(filtered)
    output_client_csv()

main()
