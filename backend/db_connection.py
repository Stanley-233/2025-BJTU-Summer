# db_connection.py
from sqlalchemy import create_engine
import pandas as pd

class DatabaseConnection:
    def __init__(self):
        self.engine = create_engine('postgresql://root:Bjtu2025@122.9.0.229/bjtu')

    def get_speed_data(self, start_date=None, end_date=None):
        if start_date and end_date:
            query = f"SELECT time_interval_start, average_speed FROM five_min_speed WHERE time_interval_start BETWEEN '{start_date}' AND '{end_date}'"
        else:
            query = "SELECT time_interval_start, average_speed FROM five_min_speed"
        df = pd.read_sql(query, self.engine)
        df['average_speed'] = df['average_speed']
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

    def get_trip_percentage_data(self, start_date=None, end_date=None):
        if start_date and end_date:
            query = f"SELECT date, medium_trip, short_trip, long_trip FROM trip_percentage WHERE date BETWEEN '{start_date}' AND '{end_date}'"
        else:
            query = "SELECT date, medium_trip, short_trip, long_trip FROM trip_percentage"
        df = pd.read_sql(query, self.engine)
        return df.to_dict(orient='records')