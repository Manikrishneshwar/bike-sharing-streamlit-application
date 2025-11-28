from packages import *

@st.cache_data  # Cache the function's output to improve performance
# Define the function to query station status from a given URL

def query_station_status(url):
    '''
    This function takes a url of the open raw data as input.
    Return type: data frame
    
    It performs cleaning and processing of the raw data where: 
        -Convert data into a data frame
        -Filter stations not renting
        -Handle missing values
        -Filter stations not returning
        -remove duplicates
        -convert timestamps datatypes into proper datetime format with UTC timezone
        -expand the bikes column 
    
    '''
    with urllib.request.urlopen(url) as data_url:  # Open the URL
        data=json.loads(data_url.read().decode())  # Read and decode the JSON data

    df=pd.DataFrame(data['data']['stations'])  # Convert the data to a Dataframe
    df=df[df.is_renting == 1]  # Filter out stations that are not renting
    df=df[df.is_returning == 1]  # Filter out stations that are not returning
    df=df.drop_duplicates(['station_id', 'last_reported'])  # Remove duplicate records
    df['time'] = data['last_updated']  # Add the last updated time to the DataFrame
    df["time"]=df["time"].map(lambda x: datetime.fromtimestamp(x, tz=timezone.utc) if not math.isnan(x) else None)
    df["last_reported"]=df["last_reported"].map(lambda x: datetime.fromtimestamp(x, tz=timezone.utc) if not math.isnan(x) else None) # Convert timestamps to datetime
    df=df.set_index('time')  # Set the time as the index
    df=pd.concat([df, df['num_bikes_available_types'].apply(pd.Series)], axis=1)  #Expand bike column fr easier access.

    return df  # Return the Dataframe

# Define the function to get station latitude and longitude from a given URL
def get_station_latlon(url):
    '''
    Input parameter: URL for raw open data
    Return type: Dataframe
    
    This function decodes JSON data to get the latitude and longitude of the stations and returns this in a dataframe. 
    '''
    with urllib.request.urlopen(url) as data_url:  # Open the URL
        latlon=json.loads(data_url.read().decode())  # Read and decode the JSON data
    latlon=pd.DataFrame(latlon['data']['stations'])  # Convert the data to a Dataframe
    return latlon  # Return the Dataframe

# Define the function to join two DataFrames on station_id
def join_latlon(df1, df2):
    '''
    Input parameters: Dataframe df1, Dataframe df2
    Return Type: Dataframe
    
    Merges the 2 input dataframes (left join) on station_id and return the merged dataframe.
    '''
    df=df1.merge(df2[['station_id', 'lat', 'lon']], 
                how='left', 
                on='station_id')  # Merge the Dataframes on station_id
    return df  # Return the merged Dataframe

# Function to determine marker color based on the number of bikes available
def get_marker_color(num_bikes_available):
    '''
    Input params: number of bikes available
    Return type: string
    
    Takes in the number of bikes available and return a color corresponding to some conditions based on number of bikes.
    '''
    if num_bikes_available > 3:
        return 'green'
    elif 0 < num_bikes_available <= 3:
        return 'yellow'
    else:
        return 'red'

# Define the function to geocode an address
def geocode(address):
    '''
    Input parameter: Address (string of format "<street name> <city name> <country name>")
    Return type: Tuple (Latitude, Longitude) OR None
    
    Uses geolocator to locate an address and return the cordinates if found. Else None is returned.
    '''
    geolocator = Nominatim(user_agent="clicked-demo")  # Create a geolocator object
    location = geolocator.geocode(address)  # Geocode the address
    if location is None:
        return ''  # Return an empty string if the address is not found
    else:
        return (location.latitude, location.longitude)  # Return the latitude and longitude
    
# Define the function to get bike availability near a location
def get_bike_availability(latlon, df, input_bike_modes):
    """
    Input parameters: Tuple->(Latitude,Longitude), dataframe, List
    Return Type: List ->[station_id, Latitude, Longitude]
    
    Calculate distance from each station to the user and return closest viable station details
    """
    if len(input_bike_modes) == 0 or len(input_bike_modes) == 2:  # If no mode selected, assume both bikes are selected
        i = 0
        df['distance'] = ''
        while i < len(df):
            df.loc[i, 'distance'] = geodesic(latlon, (df['lat'][i], df['lon'][i])).km  # Calculate distance to each station
            i = i + 1
        df = df.loc[(df['ebike'] > 0) | (df['mechanical'] > 0)]  # Remove stations with no available bikes
        chosen_station = []
        chosen_station.append(df[df['distance'] == min(df['distance'])]['station_id'].iloc[0])  # Get closest station
        chosen_station.append(df[df['distance'] == min(df['distance'])]['lat'].iloc[0])
        chosen_station.append(df[df['distance'] == min(df['distance'])]['lon'].iloc[0])
    else:
        i = 0
        df['distance'] = ''
        while i < len(df):
            df.loc[i, 'distance'] = geodesic(latlon, (df['lat'][i], df['lon'][i])).km  # Calculate distance to each station
            i = i + 1
        df = df.loc[df[input_bike_modes[0]] > 0]  # Remove stations without the selected mode available
        chosen_station = []
        chosen_station.append(df[df['distance'] == min(df['distance'])]['station_id'].iloc[0])  # Get closest station
        chosen_station.append(df[df['distance'] == min(df['distance'])]['lat'].iloc[0])
        chosen_station.append(df[df['distance'] == min(df['distance'])]['lon'].iloc[0])
    return chosen_station  # Return the chosen station

# Define the function to get dock availability near a location
def get_dock_availability(latlon, df):
    """
    Input parameters:Tuple with (Latitude,Longitude), Dataframe
    Return Type: List ->[station_id, Latitude, Longitude]
    
    Calculate distance from each station to the user and return details of closest station station
    """
    i = 0
    df['distance'] = ''
    while i < len(df):
        df.loc[i, 'distance'] = geodesic(latlon, (df['lat'][i], df['lon'][i])).km  # Calculate distance to each station
        i = i + 1
    df = df.loc[df['num_docks_available'] > 0]  # Remove stations without available docks
    chosen_station = []
    chosen_station.append(df[df['distance'] == min(df['distance'])]['station_id'].iloc[0])  # Get closest station
    chosen_station.append(df[df['distance'] == min(df['distance'])]['lat'].iloc[0])
    chosen_station.append(df[df['distance'] == min(df['distance'])]['lon'].iloc[0])

    return chosen_station  # Return the chosen station

# Define the function to run OSRM and get route coordinates and duration
def run_osrm(chosen_station, iamhere):
    '''
    Input params: List->[station_id, Latitude, Longitude], Tuple->(Latitude,Longitude)
    Return Type: List of coordinates, float duration
    
    Takes current position coords, and destination coords to calculate 
    the route and the time taken to get to destination
    '''
    start = "{},{}".format(iamhere[1], iamhere[0])  # Format the start coordinates
    end = "{},{}".format(chosen_station[2], chosen_station[1])  # Format the end coordinates
    url = 'http://router.project-osrm.org/route/v1/driving/{};{}?geometries=geojson'.format(start, end)  # Create the OSRM API URL

    headers = {'Content-type': 'application/json'}
    r = requests.get(url, headers=headers)  # Make the API request
    print("Calling API ...:", r.status_code)  # Print the status code

    routejson = r.json()  # Parse the JSON response
    coordinates = []
    i = 0
    lst = routejson['routes'][0]['geometry']['coordinates']
    while i < len(lst):
        coordinates.append([lst[i][1], lst[i][0]])  # Extract coordinates
        i = i + 1
    duration = round(routejson['routes'][0]['duration'] / 60, 1)  # Convert duration to minutes

    return coordinates, duration  # Return the coordinates and duration