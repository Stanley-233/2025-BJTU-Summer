# db_connection.py
from sqlalchemy import create_engine
import pandas as pd

class DatabaseConnection:
    def __init__(self):
        self.engine = create_engine('postgresql://root:Bjtu2025@122.9.0.229/bjtu')

    def get_speed_data(self, start_date=None, end_date=None):
        if start_date and end_date:
            query = f"SELECT timestamp, average_speed FROM speed_data WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'"
        else:
            query = "SELECT timestamp, average_speed FROM speed_data"
        df = pd.read_sql(query, self.engine)
        # 将速度从 cm/s 转换为 km/h
        df['average_speed'] = df['average_speed'] * 0.036
        return df.to_dict(orient='records')

    def get_od_data(self, start_date=None, end_date=None):
        if start_date and end_date:
            query = f"SELECT timestamp, active_vehicles FROM vehicle_counts WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'"
        else:
            query = "SELECT timestamp, active_vehicles FROM vehicle_counts"
        df = pd.read_sql(query, self.engine)
        return df.to_dict(orient='records')

    def get_taxi_weather_data(self, start_date=None, end_date=None):
        if start_date and end_date:
            query = f"SELECT hour, active_taxis, temperature, humidity, wind_speed FROM hourly_taxi_weather WHERE hour BETWEEN '{start_date}' AND '{end_date}'"
        else:
            query = "SELECT hour, active_taxis, temperature, humidity, wind_speed FROM hourly_taxi_weather"
        df = pd.read_sql(query, self.engine)
        return df.to_dict(orient='records')