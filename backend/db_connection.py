# db_connection.py
from sqlalchemy import create_engine
import pandas as pd

class DatabaseConnection:
    def __init__(self):
        # 修改为PostgreSQL的连接字符串格式
        self.engine = create_engine('postgresql://root:Bjtu2025@122.9.0.229/bjtu')

    def get_speed_data(self, start_date=None, end_date=None):
        if start_date and end_date:
            # 使用PostgreSQL的日期格式和语法
            query = f"SELECT timestamp, average_speed FROM speed_data WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'"
        else:
            query = "SELECT timestamp, average_speed FROM speed_data"
        df = pd.read_sql(query, self.engine)
        # 将速度从cm/s转换为km/h
        df['average_speed'] = df['average_speed'] * 0.036
        return df.to_dict(orient='records')