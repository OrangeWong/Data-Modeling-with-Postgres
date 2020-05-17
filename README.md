# Overview
A startup called Sparkify wants to analyze the data they've been collecting on songs and user activity on their new music streaming app. The analytics team is particularly interested in understanding what songs users are listening to. 

Currently, their data resides in a directory of JSON logs (in data folder), which is not easy for acting analysis. Thus, this repo is to extract data from data source, to transform the data into table format, and finally to store the transformed data in a relational database for future analysis.

# Structure of the Repository
There are 6 files in the top level:
- README.md: A brief introduction of the repository.
- Notebooks:
    - etl.ipynb: A jupyter notebook for doing exploratory work on ETL process. 
    - test.ipynb: A notebook for displaying the first few rows of each table for checking the database.
- Python scripts:
    - etl.py: Implementation of ETL process.
    - create_tables.py: A script to drop tables if exists in the database and to create new tables.
    - sql_queries.py: A file that contains all the sql quesries, which are used to manipulate the database. 
    
# Usages
- Start a new terminal session in Launcher.
- run command `python create_tables.py` to setup the database.
- run command `python etl.py` to perform ETL and store the transformed data into the database.