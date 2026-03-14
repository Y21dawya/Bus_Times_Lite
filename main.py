import requests
import os
import sqlite3 as sql

os.chdir(os.path.dirname(os.path.abspath(__file__))) #Ensures the file is being run in the correct directory, so that all dependent files will be present

stops = sql.connect("stops.db") #Connecting to all of the databases
seq = sql.connect("seq.db")
tr_stops = sql.connect("tr_stops.db")

stop_ID = ""

def get_naptan(method, stop_data): #Done in a subroutine to make debugging easier
    stop_ID = ""
    if method == "1":
        if stop_data[:3] == "4900": #Checks that the naptan is a valid london code
            stop_ID = stop_data #Entered data is a NaPTAN ATCO code
    elif method == "2":
        stop_ID = stops.execute(f'SELECT Naptan_Atco FROM bus_stops WHERE Stop_Code = {stop_data}').fetchone() #Finds NaPTAN with the matching stop code
        stop_ID = str(stop_ID)[2:-3] #Slicing to remove unnecessary commas and brackets
        print(stop_ID)
    elif method == "3":
        stop_ID = stops.execute(f'SELECT Naptan_Atco FROM bus_stops WHERE Stop_Code_LBSL = {stop_data}').fetchone()
        stop_ID = str(stop_ID)[2:-3]
        print(stop_ID)
    elif method =="4":
        potential = stops.execute(f'SELECT Naptan_Atco, Heading, Stop_Name FROM bus_stops WHERE Stop_Name LIKE "%{stop_data}%"').fetchall() #Retrieves relevant data to the stop to allow the user to ensure they are choosing the correct stop
        for i in range (0,len(potential)):
            print(f"{i+1} - {potential[i]}") #Prints all matching stops' data
        selection = int(input("Please enter the number of the stop you wish to select: "))-1
        stop_ID = str(potential[selection])[2:str(potential[selection]).index(",")-1]
    else:
        print("invalid input")
    return(stop_ID)

#blah

app_id = "Bus_Times_Lite"
app_key = "f485d0c23eaa46dd8af5841ba61ece70"

method = input("What method would you like to use to find a stop? \n If you would like to enter a NaPTAN-ATCO code, please enter 1. \n If you would like to enter a 5-digit SMS code, please enter 2.\n If you would like to enter a stop code, please enter 3. \n If you would like to search for a stop, please enter 4. \n").strip()
stop_data = input("What is the relevant information about the bus stop?\n").strip().lower() #Strip and lower to sanitise input

stop_ID = get_naptan(method, stop_data)

filter_method = input("What filtering method would you like to use?\n To filter by a specific bus or buses, enter 1.\n To filter by buses calling subsequently or prequisitely at a given stop, enter 2.\n If none, leave blank\n").strip()

search_bus = [] 

if filter_method == "1":
    line_input = str(input("Please enter the line of the bus you would like to filter by:\n(to end, leave blank)\n"))
    while line_input != "": #Allows for multiple entries
        search_bus.append(line_input)
        line_input = str(input("Please enter the line of the bus you would like to filter by:\n(to end, leave blank)\n"))
        if line_input not in search_bus: #Prevents duplicate entries
            search_bus.append(line_input) #No need to check if the bus stops at both stops - If it stops at the second stop, and is filtered by, only the desired buses will be shown

if filter_method == "2":
    filter_stop_method = input("What method would you like to use to find a stop? \n If you would like to enter a NaPTAN-ATCO code, please enter 1. \n If you would like to enter a 5-digit SMS code, please enter 2.\n If you would like to enter a stop code, please enter 3. \n If you would like to search for a stop, please enter 4. \n").strip()
    filter_stop_data = input("What is the relevant information about the bus stop?\n").strip().lower()
    filter_stop_ID = get_naptan(filter_stop_method, filter_stop_data)
    buses_dest = seq.execute("SELECT Route FROM bus_sequences WHERE Naptan_Atco = ? COLLATE NOCASE",(filter_stop_ID,)).fetchall()
    
    for item in buses_dest:
        search_bus.append(str(item)[2:-3]) #Sliced to remove SQL artefacts

url = f"https://api.tfl.gov.uk/StopPoint/{stop_ID}/Arrivals?app_id={app_id}&app_key={app_key}"
response = requests.get(url)

if response.status_code == 200: #Successful response code
    data = response.json()
    if not data: #Checks for data
        print("No arrival information available.")
    for bus in data:
        if search_bus == []: #Returns all data if no filtering is present
            print(f"{bus['modeName']} {bus['lineName']} to {bus['destinationName']} arriving in {bus['timeToStation'] // 60} minutes, {bus['timeToStation'] % 60} seconds. ")
        elif bus['lineName'] in search_bus: #Filters by user-chosen buses if there are any
            print(f"{bus['modeName']} {bus['lineName']} to {bus['destinationName']} arriving in {bus['timeToStation'] // 60} minutes, {bus['timeToStation'] % 60} seconds.")
else:
    print(f"Error: {response.status_code} - {response.text}") #Otherwise gives the error