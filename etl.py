import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *
from datetime import datetime


def process_song_file(cur, filepath):
    """ Process song file when the filepath of the song file is given, 
        extract the required data from song file, and insert the data into
        database.
        
    Parameters: 
        cur (cursor): the cursor of MySQL datasbase.
        filepath (str): the filepath of the song file that to be processed.
    
    Returns:
        None
    """
    
    # open song file
    df = pd.read_json(filepath, lines=True)
    
    # insert song record
    song_cols = ["song_id", "title", "artist_id", "year", "duration"]
    song_data = list(df[song_cols].iloc[0].values)
    formats = [str, str, str, int, float]
    song_data = [f(x) for x, f in zip(song_data, formats)]
    cur.execute(song_table_insert, song_data)
    
    # insert artist record
    artist_cols = ["artist_id",  
                   "artist_name", 
                   "artist_location", 
                   "artist_latitude", 
                   "artist_longitude"]
    artist_data = list(df[artist_cols].iloc[0].values)
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    """ Process log file when the filepath of the log file is given, 
        then extract the required data from the file, and insert the 
        data into database.
        
    Parameters: 
        cur (cursor): the cursor of MySQL datasbase.
        filepath (str): the filepath of the log file that to be processed.
    
    Returns:
        None
    """
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    mask = (df['page'] == 'NextSong')
    df = df.loc[mask]

    # convert timestamp column to datetime
    t = df["ts"].apply(lambda x: datetime.fromtimestamp(x//1e3))
    
    # insert time data records
    time_data = (
        t.dt.values.astype(int) // 10**9,
        t.dt.hour, 
        t.dt.day, 
        t.dt.week, 
        t.dt.month, 
        t.dt.year,
        t.dt.weekday
    )
    column_labels = (
        'start_time', 
        'hour', 
        'day', 
        'week', 
        'month', 
        'year', 
        'weekday'
    )
    time_df = pd.DataFrame(data={col: v for col, v in zip(column_labels, time_data)})

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))
    
    # load user table
    cols = ['userId', 'firstName', 'lastName', 'gender', 'level']
    user_df = df[cols]

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():
        
        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()
        
        if results:
            songid, artistid = results
#             print(songid, artistid)
        else:
            songid, artistid = None, None

        # insert songplay record
        songplay_data = (index, 
                         row['ts']//1e3,
                         row['userId'],
                         row['level'], 
                         songid, 
                         artistid, 
                         row['sessionId'],
                         row['location'], 
                         row['userAgent']
                        )
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    """ Extract the data, and insert the processed data into the database.
    
    Parameters:
        cur (cursor): the cursor of the connection of the given database.
        conn (connection): the connection of the given database.
        filepath (str): the filepath of the data. 
        func (funciton): the function that used to process song or log files with choices
            'process_song_file' and 'process_log_file'
            
    Returns:
        None    
    """
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    """The main function to process the data and dump into the database.
    """
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()