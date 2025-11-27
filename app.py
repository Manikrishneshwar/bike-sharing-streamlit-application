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
