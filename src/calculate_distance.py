#%%
import pandas as pd
import googlemaps
import datetime
from tqdm import tqdm
from dotenv import load_dotenv
import os
load_dotenv()

#%%
PROPERTIES_FILE_PATH = '../properties.csv'
GOOGLE_MAP_API_KEY = os.environ.get('GOOGLE_MAP_API_KEY')
ORIGIN = "Downtown Toronto, Old Toronto, Toronto, ON"
OUTPUT_FILE_PATH = '../properties_with_distance.csv'
DEPARTURE_TIME = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=3), datetime.time(hour=8))
CHUNK_SIZE = 25

#%%
gmaps = googlemaps.Client(key=GOOGLE_MAP_API_KEY)
df = pd.read_csv(PROPERTIES_FILE_PATH)
df = df[df['address'].notna()]
df.head()

#%%
def tryCatch(function):
    try:
        return function()
    except:
        return None
    

def duration_to_minutes(duration_str):
    # Split the duration string into components
    components = duration_str.split()

    # Convert each component to minutes
    total_minutes = 0
    for i in range(len(components)):
        if components[i] == 'hour' or components[i] == 'hours':
            total_minutes += int(components[i-1]) * 60
        elif components[i] == 'min' or components[i] == 'mins':
            total_minutes += int(components[i-1])

    return int(total_minutes)

#%%
results = []

for i in tqdm(range(0, df.shape[0], CHUNK_SIZE)):
    df_chunk = df.iloc[i:i+CHUNK_SIZE]
    destinations = df_chunk['address'].tolist()
    transit_directions = gmaps.distance_matrix(origins=[ORIGIN],
                               destinations=destinations,
                               mode='transit',
                               units="metric",
                               language="en-US",
                               departure_time=DEPARTURE_TIME)
    driving_directions = gmaps.distance_matrix(origins=[ORIGIN],
                               destinations=destinations,
                               mode='driving',
                               units="metric",
                               language="en-US",
                               departure_time=DEPARTURE_TIME,
                               avoid="tolls")
    
    for i in range(len(destinations)):
        df_row = df_chunk.iloc[i]
        df_row['transit_duration'] = tryCatch(lambda: transit_directions['rows'][0]['elements'][i]['duration']['text'])
        df_row['transit_distance'] = tryCatch(lambda: transit_directions['rows'][0]['elements'][i]['distance']['text'])
        df_row['driving_duration'] = tryCatch(lambda: driving_directions['rows'][0]['elements'][i]['duration']['text'])
        df_row['driving_distance'] = tryCatch(lambda: driving_directions['rows'][0]['elements'][i]['distance']['text'])
        results.append(df_row)


#%%
df = pd.DataFrame(results)
results = []
for idx, row in df.iterrows():
    row['transit_duration_min'] = None
    row['driving_duration_min'] = None
    if row['transit_duration'] is not None and isinstance(row['transit_duration'], str):
        row['transit_duration_min'] = duration_to_minutes(row['transit_duration'])
    if row['driving_duration'] is not None and isinstance(row['driving_duration'], str):
        row['driving_duration_min'] = duration_to_minutes(row['driving_duration'])
    results.append(row)

df = pd.DataFrame(results)
df.to_csv(OUTPUT_FILE_PATH, index=False)


# %%
