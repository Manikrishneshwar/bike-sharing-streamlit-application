from helpers import *
from packages import *

station_url='https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_status'
latlon_url='https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_information'

# data preprocessing. In this we take data by scrapping the open data for bike share in the city of torronto.
# We then process this raw data, changing the time nto date time format of UTC timezone, remove duplicates, 
# handle missing values and then finally join 2 data frames to get our complete dataset for this project.
data_df=query_station_status(station_url)
latlon_df=get_station_latlon(latlon_url)
data=join_latlon(data_df,latlon_df)

# variables
findmeabike,findmeadock=False,False

# Stream lit application code starts here
st.title('Torronto Bike Share Station Status')
st.markdown('This dashboard tracks bike availability at each bike share station in Torronto.')

# We create columns for the dashboard in order to display some metrics.
# the metrics displayed are number of availability of bikes, and number 
# of stations with availability of bikes and docks.
col1,col2,col3=st.columns(3)
with col1:
    st.metric(label='Bikes Available Now',value=sum(data['num_bikes_available']))
    st.metric(label='EBikes Available Now',value=sum(data['ebike']))
with col2:
    st.metric(label='Stations w Available Bikes',value=len(data[data['num_bikes_available']>0]))
    st.metric(label='Stations w Available E-bikes',value=len(data[data['ebike']>0]))
with col3:
    st.metric(label='Stations w Empty Docks',value=len(data[data['num_docks_available']>0]))


with st.sidebar:
    rent_return=st.selectbox(
        "Are you looking to rent or return a bike?",
        ("Rent","Return")
    )
    if rent_return=="Rent":
        input_bike_modes=st.multiselect(
            'What kind of bikes are you loooking to rent?',
            ['ebike','mechanical']
        )
        st.header("Where are you located?")
        input_street=st.text_input("Street","")
        input_city=st.text_input("City","Toronto")
        input_country=st.text_input("Country","Canada")
        drive=st.checkbox("I'm driving here.")
        findmeabike=st.button("Find me a bike!",type='primary')
        
        
        if findmeabike:
            if input_street!="":
                iamhere=geocode(input_street+" "+input_city+" "+input_country)
                
                # handling edge case scenario where user input location is incorrect.
                if iamhere=='':
                    st.subheader(':red[Input address not valid!]')
                    
            # handling edge case scenario where no input from user
            else:
                st.subheader(':red[Input address not valid!]')
    
    elif rent_return=="Return":
        st.header("Where are you located?")
        input_street_return=st.text_input("Street","")
        input_city=st.text_input("City","Toronto")
        input_country=st.text_input("Country","Canada")
        drive=st.checkbox("I'm driving here.")
        findmeadock=st.button("Find me a dock!",type='primary')
        
        
        if findmeadock:
            if input_street_return!="":
                iamhere_return=geocode(input_street_return+" "+input_city+" "+input_country)
                
                # handling edge case scenario where user input location is incorrect.
                if iamhere_return=='':
                    st.subheader(':red[Input address not valid!]')
                    
            # handling edge case scenario where no input from user
            else:
                st.subheader(':red[Input address not valid!]')


if rent_return=="Return" and findmeadock==False:
    #folium map centered around the city of Toronto
    center=[43.65306613746548,-79.38815311015] #coords for toronto
    m=folium.Map(location=center,zoom_start=13,tiles='cartodbpositron') #create map with grey background

    for _,row in data.iterrows():
        marker_color=get_marker_color(row['num_bikes_available'])
        folium.CircleMarker(
            location=[row['lat'],row['lon']],
            radius=2,
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.7,
            popup=folium.Popup(f"Station ID: {row['station_id']}<br>"
                            f"Total Bikes Available: {row['num_bikes_available']}<br>"
                            f"Mechanical Bikes Available: {row['mechanical']}<br>"
                            f"E-bikes Available: {row['ebike']}",max_width=300)
            ).add_to(m)
        
    # display map in streamlit web app
    folium_static(m)
    
if rent_return=="Rent" and findmeabike==False:              
    #folium map centered around the city of Toronto
    center=[43.65306613746548,-79.38815311015] #coords for toronto
    m=folium.Map(location=center,zoom_start=13,tiles='cartodbpositron') #create map with grey background

    for _,row in data.iterrows():
        marker_color=get_marker_color(row['num_bikes_available'])
        folium.CircleMarker(
            location=[row['lat'],row['lon']],
            radius=2,
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.7,
            popup=folium.Popup(f"Station ID: {row['station_id']}<br>"
                            f"Total Bikes Available: {row['num_bikes_available']}<br>"
                            f"Mechanical Bikes Available: {row['mechanical']}<br>"
                            f"E-bikes Available: {row['ebike']}",max_width=300)
            ).add_to(m)
        
    # display map in streamlit web app
    folium_static(m)
    
if findmeabike:
    if input_street!='':
        if iamhere!='':
            chosen_station=get_bike_availability(iamhere,data,input_bike_modes)
            center=iamhere
            m1=folium.Map(location=center,zoom_start=16,tiles="cartodbpositron")
            for _,row in data.iterrows():
                marker_color=get_marker_color(row['num_bikes_available'])
                folium.CircleMarker(
                    location=[row['lat'],row['lon']],
                    radius=2,
                    color=marker_color,
                    fill=True,
                    fill_color=marker_color,
                    fill_opacity=0.7,
                    popup=folium.Popup(f"Station ID: {row['station_id']}<br>"
                                    f"Total Bikes Available: {row['num_bikes_available']}<br>"
                                    f"Mechanical Bikes Available: {row['mechanical']}<br>"
                                    f"E-bikes Available: {row['ebike']}",max_width=300)
                    ).add_to(m1)
            # marker to indicate user position
            folium.Marker(
                location=iamhere,
                popup="You are here.",
                icon=folium.Icon(color="blue",icon="person",prefix="fa")
            ).add_to(m1)
            #Marker to indicate destination
            folium.Marker(
               location= (chosen_station[1],chosen_station[2]),
               popup="Rent bike here.",
               icon=folium.Icon(color="red",icon="bicycle",prefix="fa")
            ).add_to(m1)
            #get duration for getting to closest station to rent
            coordinates,duration=run_osrm(chosen_station,iamhere)
            
            #create a path with the shortest distance and display time as well
            folium.PolyLine(
                locations=coordinates,
                color="blue",
                weight=5,
                tooltip="{} mins away from destination.".format(duration)
            ).add_to(m1)
            folium_static(m1)
            with col3:
                st.metric(label=":green[Travel Time (min)]",value=duration) #display travel time

if findmeadock:
    if input_street_return!='':
        if iamhere_return!='':
            chosen_station=get_dock_availability(iamhere_return,data)
            center=iamhere_return
            m1=folium.Map(location=center,zoom_start=16,tiles="cartodbpositron")
            for _,row in data.iterrows():
                marker_color=get_marker_color(row['num_bikes_available'])
                folium.CircleMarker(
                    location=[row['lat'],row['lon']],
                    radius=2,
                    color=marker_color,
                    fill=True,
                    fill_color=marker_color,
                    fill_opacity=0.7,
                    popup=folium.Popup(f"Station ID: {row['station_id']}<br>"
                                    f"Total Bikes Available: {row['num_bikes_available']}<br>"
                                    f"Mechanical Bikes Available: {row['mechanical']}<br>"
                                    f"E-bikes Available: {row['ebike']}",max_width=300)
                    ).add_to(m1)
            # marker to indicate user position
            folium.Marker(
                location=iamhere_return,
                popup="You are here.",
                icon=folium.Icon(color="blue",icon="person",prefix="fa")
            ).add_to(m1)
            #Marker to indicate destination
            folium.Marker(
               location= (chosen_station[1],chosen_station[2]),
               popup="Return bike here.",
               icon=folium.Icon(color="red",icon="bicycle",prefix="fa")
            ).add_to(m1)
            #get duration for getting to closest station to rent
            coordinates,duration=run_osrm(chosen_station,iamhere_return)
            
            #create a path with the shortest distance and display time as well
            folium.PolyLine(
                locations=coordinates,
                color="blue",
                weight=5,
                tooltip="{} mins away from destination.".format(duration)
            ).add_to(m1)
            folium_static(m1)
            with col3:
                st.metric(label=":green[Travel Time (min)]",value=duration) #display travel time