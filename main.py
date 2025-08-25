import requests
import asyncio
import pandas as pd

tr_stops = pd.read_csv("NUMBAT NaPTANs.csv")
seq = pd.read_csv("bus-sequences.csv")
stops = pd.read_csv("bus-stops.csv")

stop_ID = ""

async def sms_to_naptan(sms):
    global stop_ID
    for _, stop in stops.iterrows():
        if str(stop['Bus_Stop_Code']) == sms:
            stop_ID = stop['Naptan_Atco']

async def stop_code_to_naptan(code):
    global stop_ID
    for _, stop in stops.iterrows():
        if str(stop['Stop_Code_LBSL']) == code:
            stop_ID = stop['Naptan_Atco']

async def stop_search(name):
    global stop_ID
    global candidates
    global final
    final = []
    candidates = []
    for _, stop in stops.iterrows():
        for item in name.lower().split():
            if item in stop['Stop_Name'].lower().split():
                candidates.append(stop['Stop_Name'])
    for item in candidates:
        if name in item.lower():
            final.append(item)
    print(", ".join(final))

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
search_bus = input("What bus are you searching for? (if none, leave blank) \n").strip()

url = f"https://api.tfl.gov.uk/StopPoint/{stop_ID}/Arrivals?app_id={app_id}&app_key={app_key}"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    if not data:
        print("No arrival information available.")
    for bus in data:
        if search_bus == "":
            print(f"{bus['modeName']} {bus['lineName']} to {bus['destinationName']} arriving in {bus['timeToStation'] // 60} minutes, {bus['timeToStation'] % 60} seconds. ")
        elif bus['lineName'] == search_bus:
            print(f"{bus['modeName']} {bus['lineName']} to {bus['destinationName']} arriving in {bus['timeToStation'] // 60} minutes, {bus['timeToStation'] % 60} seconds.")
else:
    print(f"Error: {response.status_code} - {response.text}")