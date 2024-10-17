import pandas as pd
from sqlalchemy import create_engine

username = 'root'
password = 'ngfw123!%40%23'
port = '3306'
host = '10.113.53.29'
database = 'true_zentao_copy'


engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}')



df = pd.read_sql_query('SELECT * FROM zt_bug', engine)

print(df.head())