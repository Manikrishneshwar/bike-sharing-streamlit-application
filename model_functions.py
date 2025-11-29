from params import *
from packages import *
dfs=[]

def read_data():
    '''
    Input params: None
    Return Type: Dataframe
    
    This function reads from over 50 csv files, cleans any unrecognized rows by utf-8 decoding 
    and then combines all of them into a single csv file. This csv file is written as "combined_clean.csv"
    If 'combined_clean.csv' is already present, then it directly reads the csv file and returns it as a dataframe
    '''
    if os.path.isfile(combined_file):
        return pd.read_csv(combined_file, na_values=['NULL','','null'],low_memory=False)
    
    else:
        for fname in os.listdir(directory_path):
            if not fname.endswith(".csv"):
                continue
            cleanlines=[]
            path=os.path.join(directory_path, fname)
            
            print("Processing: ",fname)
            
            with open(path,'rb') as f:
                for line in f:
                    try:
                        cleanlines.append(line.decode("utf-8"))
                    except UnicodeDecodeError:
                        continue
            df=pd.read_csv(StringIO("".join(cleanlines)))
            dfs.append(df)

        final=pd.concat(dfs,ignore_index=True)
        final.to_csv(combined_file,index=False)
        return final


def clean(data):
    '''
    Input-> Dataframe
    Return Type-> Data frame
    
    Cleans the dataframe by removing duplicates, and converting timestamps into date time format.
    creates separate column for easier access.
    '''
    df = data.copy()   # <--- fixes warning

    df = df.drop_duplicates(subset=["Trip Id"])

    # Convert the string datetime columns to actual datetimes
    df["Start Time"] = pd.to_datetime(
        df["Start Time"], format="%m/%d/%Y %H:%M", errors="coerce"
    )
    df["End Time"] = pd.to_datetime(
        df["End Time"], format="%m/%d/%Y %H:%M", errors="coerce"
    )

    # Drop rows that failed to parse
    df = df.dropna(subset=["Start Time", "End Time"])
    df["start_hour"] = df["Start Time"].dt.hour
    df["start_day"] = df["Start Time"].dt.day
    df["start_month"] = df["Start Time"].dt.month
    df["start_dow"] = df["Start Time"].dt.dayofweek
    return df