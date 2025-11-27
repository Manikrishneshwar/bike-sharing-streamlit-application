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