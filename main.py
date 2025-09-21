import requests
import asyncio
import pandas as pd
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

tr_stops = pd.read_csv("train stops.csv")
seq = pd.read_csv("bus-sequences.csv")
stops = pd.read_csv("bus-stops.csv")

stop_ID = ""

def sms_to_naptan(sms):
    global stop_ID
    for _, stop in stops.iterrows():
        if str(stop['Bus_Stop_Code']) == sms:
            stop_ID = stop['Naptan_Atco']

def stop_code_to_naptan(code):
    global stop_ID
    for _, stop in stops.iterrows():
        if str(stop['Stop_Code_LBSL']) == code:
            stop_ID = stop['Naptan_Atco']

def stop_search(name):
    global stop_ID
    global list
    list = [[],[],[]]
    for _, stop in stops.iterrows():
        search = True
        for word in name.lower().split():
            if word not in stop['Stop_Name'].lower().split():
                search = False
        if search:
            stop_direction = ""
            if stop['Heading'] < 23 and stop['Heading'] > 337:
                stop_direction = " Northbound"
            elif stop['Heading'] < 68 and stop['Heading'] > 22: 
                stop_direction = " Northeastbound"
            elif stop['Heading'] < 113 and stop['Heading'] > 67:
                stop_direction = " Eastbound"
            elif stop['Heading'] < 158 and stop['Heading'] > 112:
                stop_direction = " Southeastbound"
            elif stop['Heading'] < 203 and stop['Heading'] > 157:
                stop_direction = " Southbound"
            elif stop['Heading'] < 248 and stop['Heading'] > 202:
                stop_direction = " Southwestbound"
            elif stop['Heading'] < 293 and stop['Heading'] > 247:
                stop_direction = " Westbound"
            elif stop['Heading'] < 338 and stop['Heading'] > 292:
                stop_direction = " Northwestbound"
            list[0].append(stop['Stop_Name'])
            list[1].append(stop['Naptan_Atco'])
            list[2].append(stop_direction)
    for i in range(len(list[0])):
        print(f"{i+1}. {list[0][i]}, {list[1][i]}, {list[2][i]}")
    choice = int(input("Please enter the number of the stop you want to use: \n").strip())
    stop_ID = list[1][choice-1]

app_id = "Bus_Times_Lite"
app_key = "f485d0c23eaa46dd8af5841ba61ece70"

method = input("What method would you like to use to find a stop? \n If you would like to enter a NaPTAN-ATCO code, please enter 1. \n If you would like to enter a 5-digit SMS code, please enter 2.\n If you would like to enter a stop code, please enter 3. \n If you would like to search for a stop, please enter 4. \n").strip()
stop_data = input("What is the relevant information about the bus stop?\n").strip().lower()

if method == "1":
    stop_ID = stop_data
elif method == "2":
    sms_to_naptan(stop_data)
elif method == "3":
    stop_code_to_naptan(stop_data)
elif method =="4":
    stop_search(stop_data)
else:
    print("invalid input")
if input("Would you like to filter buses? Y/N\n").strip().upper() == "Y":
    search_bus = input("What bus number would you like to filter for?\n").strip()
else:
    search_bus = ""

url = f"https://api.tfl.gov.uk/StopPoint/{stop_ID}/Arrivals?app_id={app_id}&app_key={app_key}"
response = requests.get(url)
if response.status_code == 200:
    print(f"According to {url}, the following buses are arriving at stop {stop_ID}:")
    data = response.json()
    if not data:
        print("No arrival information available.")
    for bus in data:
        if search_bus == "":
            print(f"{bus['modeName']} {bus['lineName']} to {bus['destinationName']} arriving in {bus['timeToStation'] // 60} minutes, {bus['timeToStation'] % 60} seconds, numberplate {bus['vehicleId']}.")
        elif bus['lineName'] == search_bus:
            print(f"{bus['modeName']} {bus['lineName']} to {bus['destinationName']} arriving in {bus['timeToStation'] // 60} minutes, {bus['timeToStation'] % 60} seconds, numberplate {bus['vehicleId']}.")
else:
    print(f"Error: {response.status_code} - {response.text}")