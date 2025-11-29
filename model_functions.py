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


