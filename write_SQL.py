import sqlite3
import datetime
from sense_emu import SenseHat
import time
import requests
import json
import random

sense=SenseHat()
backup_data={"latitude":45.82,"longitude":15.98,"generationtime_ms":0.10502338409423828,"utc_offset_seconds":0,"timezone":"GMT","timezone_abbreviation":"GMT","elevation":137.0,"current_units":{"time":"iso8601","interval":"seconds","temperature_2m":"°C","relative_humidity_2m":"%","surface_pressure":"hPa","wind_speed_10m":"km/h"},"current":{"time":"2024-07-09T01:00","interval":900,"temperature_2m":24.4,"relative_humidity_2m":74,"surface_pressure":1000.5,"wind_speed_10m":1.8},"hourly_units":{"time":"iso8601","temperature_2m":"°C","relative_humidity_2m":"%","precipitation_probability":"%"},"hourly":{"time":["2024-07-09T00:00","2024-07-09T01:00","2024-07-09T02:00","2024-07-09T03:00","2024-07-09T04:00","2024-07-09T05:00","2024-07-09T06:00","2024-07-09T07:00","2024-07-09T08:00","2024-07-09T09:00","2024-07-09T10:00","2024-07-09T11:00","2024-07-09T12:00","2024-07-09T13:00","2024-07-09T14:00","2024-07-09T15:00","2024-07-09T16:00","2024-07-09T17:00","2024-07-09T18:00","2024-07-09T19:00","2024-07-09T20:00","2024-07-09T21:00","2024-07-09T22:00","2024-07-09T23:00"],"temperature_2m":[25.5,24.4,23.0,22.9,22.5,23.4,25.2,27.0,28.8,30.0,31.1,32.1,32.9,33.7,33.9,34.2,34.0,33.7,32.2,30.3,29.2,28.8,28.3,27.4],"relative_humidity_2m":[66,74,84,83,86,79,71,67,57,55,52,47,48,43,43,41,41,40,49,53,52,56,58,61],"precipitation_probability":[0,3,7,10,8,5,3,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}}


class DataBaseManager:
	"""
	a base class representing a database table with functionalities"
	"""
	database_name="sense_db.db"
	def __init__(self,table_name,create_table_query,insert_query,read_query):
		self.table_name = table_name
		self.create_table_query = create_table_query
		self.insert_query = insert_query
		self.read_query=read_query
		self.initialize_table()
	
	def initialize_table(self):
		try:
			sc=sqlite3.connect(self.database_name)
			cursor=sc.cursor()
			cursor.execute(self.create_table_query)
			sc.commit()
			cursor.close()
			sc.close()
			print(f"table {self.table_name} initialized successfully")
			
		except sqlite3.Error as e:
			print(f"SQL error during table initialization: {e}")
			
			
	def insert_data(self,data):
		try:
			sc=sqlite3.connect(self.database_name)
			cursor=sc.cursor()
			cursor.execute(self.insert_query,data)
			sc.commit()
			cursor.close()
			sc.close()
			
		except sqlite3.Error as e:
			print(f"SQL error during table insert: {e}")
	def read_data(self):
		try:
			sc=sqlite3.connect(self.database_name)
			cursor=sc.cursor()
			cursor.execute(self.read_query)
			last_row=cursor.fetchone()
			sc.commit()
			cursor.close()
			sc.close()
			
		except sqlite3.Error as e:
			print(f"SQL error during table read: {e}")		

		return last_row
			
		
#instance with data from sense hat
class SenseHatInfo(DataBaseManager):
	def __init__(self,table_name,create_table_query,insert_query,read_query):
		super().__init__(table_name,create_table_query,insert_query,read_query)
		self.t = None
		self.p = None
		self.h = None
		
				
	def read_sensor(self):
		self.t=round(sense.get_temperature(),0)
		self.p=round(sense.pressure,0)
		self.h=round(sense.humidity,0)

	def insert_in_database(self):
		self.read_sensor()
		time_str=str(datetime.datetime.now().strftime("%H:%M %d.%m.%y"))
		data=[time_str,self.t,self.p,self.h]
		self.insert_data(data)


#instance with data from weather api
class CurrentWeather(DataBaseManager):
	def __init__(self,table_name,create_table_query,insert_query,read_query):
		super().__init__(table_name,create_table_query,insert_query,read_query)
	
	def fetch_weather(self)-> dict:

		try:
			url3="https://api.open-meteo.com/v1/forecast?latitude=45.8144&longitude=15.978&current=temperature_2m,relative_humidity_2m,precipitation,rain,cloud_cover,surface_pressure,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,rain,snowfall,cloud_cover,wind_speed_10m,uv_index&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset&timezone=Europe%2FLondon&forecast_days=3"
			response=requests.get(url3)
			return json.loads(response.text)
		except Exception as e:
			print(f"exception has occured in open meteo class: {e}")
			print("giving backup data")
			return backup_data
	
	def weather_values(self,data):
		try:
			temperature=data["current"]["temperature_2m"]
			humidity=data["current"]["relative_humidity_2m"]
			pressure=data["current"]["surface_pressure"]
			wind=data["current"]["wind_speed_10m"]
			time_str=str(datetime.datetime.now().strftime("%H:%M %d.%m.%y"))			
		except Exception as e:
			print(f"weather values function has an error: {e}")
			time_str=str(datetime.datetime.now().strftime("%H:%M %d.%m.%y"))				
			return time_str,0,0,0,0
		return time_str,temperature,humidity,pressure,wind

	def insert_in_database(self):
		weather_data=self.weather_values(self.fetch_weather())
		if weather_data:
			data_with_id=weather_data
			self.insert_data(data_with_id)


		

class ForecastWeather(DataBaseManager):
    def __init__(self):
        self.table_name="open_meteo_forecast"
        self.dataset={"time":[],"temperature":[],"humidity":[],"precipitation":[],"wind speed":[],"UV index":[],"cloud cover":[]}

        self.conn = sqlite3.connect('sense_db.db')
        self.cursor = self.conn.cursor()
        self.create_table_if_not_exists()


    def fetch_weather(self):
        try:
            url = "https://api.open-meteo.com/v1/forecast?latitude=45.8144&longitude=15.978&current=temperature_2m,relative_humidity_2m,precipitation,rain,cloud_cover,surface_pressure,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,rain,snowfall,cloud_cover,wind_speed_10m,uv_index&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset&timezone=Europe%2FLondon&forecast_days=3"
            response = requests.get(url)
            return json.loads(response.text)
        except Exception as e:
            print(f"Exception occurred in fetch_weather: {e}")
            return None
        
    def weather_values(self):
        data=self.fetch_weather()
        #print(f"forecast data {data}")
        try:
            self.dataset["time"]=data["hourly"]["time"]
            self.dataset["temperature"]=data["hourly"]["temperature_2m"]
            self.dataset["humidity"]=data["hourly"]["temperature_2m"]
            self.dataset["precipitation"]=data["hourly"]["temperature_2m"]
            self.dataset["wind speed"]=data["hourly"]["wind_speed_10m"]
            self.dataset["UV index"]=data["hourly"]["uv_index"]
            self.dataset["cloud cover"]=data["hourly"]["cloud_cover"]	
        except Exception as e:
            print(f"Forecast weather values function has an error: {e}")	
        finally:
            self.update_database()
	
    def create_table_if_not_exists(self):
        create_table_query = f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                temperature REAL,
                humidity REAL,
                precipitation REAL,
                wind_speed REAL,
                uv_index REAL,
                cloud_cover REAL
            );
        '''
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def update_database(self):
        try:
            for i in range(len(self.dataset["time"])):
                timestamp = self.dataset["time"][i]
                temperature = self.dataset["temperature"][i]
                humidity = self.dataset["humidity"][i]
                precipitation = self.dataset["precipitation"][i]
                wind_speed = self.dataset["wind speed"][i]
                uv_index = self.dataset["UV index"][i]
                cloud_cover = self.dataset["cloud cover"][i]
                # Check if timestamp exists in database
                self.cursor.execute(f'SELECT COUNT(*) FROM {self.table_name} WHERE timestamp = ?', (timestamp,))
                count = self.cursor.fetchone()[0]

                if count > 0:
                    # Update existing record
                    self.cursor.execute(f'''
                        UPDATE {self.table_name}
                        SET temperature = ?,
                            humidity = ?,
                            precipitation = ?,
                            wind_speed = ?,
                            uv_index = ?,
                            cloud_cover = ?
                        WHERE timestamp = ?
                    ''', (temperature, humidity, precipitation, wind_speed, uv_index, cloud_cover, timestamp))
                else:
                    # Insert new record
                    self.cursor.execute(f'''
                        INSERT INTO {self.table_name} (timestamp, temperature, humidity, precipitation, wind_speed, uv_index, cloud_cover)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (timestamp, temperature, humidity, precipitation, wind_speed, uv_index, cloud_cover))

                self.conn.commit()
				
        except sqlite3.Error as e:
            print(f"Error updating/inserting into database: {e}")
			                

    def read_forecast(self):
        query='''
            SELECT * FROM open_meteo_forecast;
                '''
        try:
            self.cursor.execute(query)
            rows=self.cursor.fetchall()
            timestamp_r=[]
            temperature_r=[]
            humidity_r=[]
            precipitation_r=[]
            wind_speed_r=[]
            uv_index_r=[]
            cloud_cover_r=[]
            
            for row in rows:
                dt=datetime.datetime.strptime(str(row[1]), "%Y-%m-%dT%H:%M")
                output_timestamp=f"{dt.hour}:{dt.minute}0 {dt.day}.{dt.month}"
                timestamp_r.append(str(output_timestamp))
                temperature_r.append(row[2])
                humidity_r.append(row[3])
                precipitation_r.append(row[4])
                wind_speed_r.append(row[5])
                uv_index_r.append(row[6])
                cloud_cover_r.append(row[7])

            return {
                 "Time":timestamp_r,
                 "Temperature":temperature_r,
                 "Humidity":humidity_r,
                 "Precipitation":precipitation_r,
                 "Wind speed":wind_speed_r,
                 "UV index":uv_index_r,
                 "Cloud covers":cloud_cover_r}
              
        except sqlite3.Error as e:
             print(f"error reading forecast {e}")
             return {
                 "Time":[],
                 "Temperature":[],
                 "Humidity":[],
                 "Precipitation":[],
                 "Wind speed":[],
                 "UV index":[],
                 "Cloud covers":[]}


class SimInside(DataBaseManager):
    def __init__(self):

        self.table_name="sim_inside_data"
        self.create_table_query=f'''CREATE TABLE IF NOT EXISTS {self.table_name}(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    temperature_in REAL,
                    humidity_in REAL,
                    airquality_in REAL);'''
        self.insert_query=f'''INSERT INTO {self.table_name} (timestamp,temperature_in,humidity_in,airquality_in)
                    VALUES (?,?,?,?);'''
        self.read_query=f'''SELECT * FROM {self.table_name} ORDER BY id DESC LIMIT 1'''
        super().__init__(self.table_name,self.create_table_query,self.insert_query,self.read_query)		
        self.t = 20
        self.h = 10
        self.aq= 40
        sense.stick.direction_up=self.read_sticks
        sense.stick.direction_down=self.read_sticks
        sense.stick.direction_left=self.read_sticks
        sense.stick.direction_right=self.read_sticks
        sense.stick.direction_middle=self.read_sticks

    def read_sticks(self,event):
        if event.action == "pressed":
            if event.direction == "up":
                self.t = self.t + 1
            if event.direction == "down":
                self.t = self.t - 1
        if event.action == "pressed":
            if event.direction == "left":
                self.h = self.h - 1
            if event.direction == "right":
                self.h = self.h + 1
        if event.action =="pressed":
            if event.direction == "middle":
                print("middle")
                self.aq = random.randint(20,60)

    def insert_in_database(self):
        time_str=str(datetime.datetime.now().strftime("%H:%M %d.%m.%y"))
        data=[time_str,self.t,self.h,self.aq]
        self.insert_data(data)

class SimOutside(DataBaseManager):
    def __init__(self):
        self.table_name="sim_outside_data"
        self.create_table_query=f'''CREATE TABLE IF NOT EXISTS {self.table_name}(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    temperature_out REAL,
                    wind_out REAL,
                    precipitation_out REAL);'''
        self.insert_query=f'''INSERT INTO {self.table_name} (timestamp,temperature_out,wind_out,precipitation_out)
                    VALUES (?,?,?,?);'''
        self.read_query=f'''SELECT * FROM {self.table_name} ORDER BY id DESC LIMIT 1'''
        super().__init__(self.table_name,self.create_table_query,self.insert_query,self.read_query)		
        self.t = None
        self.p = None
        self.h = None
		
    def press_to_precipitation(self):
        precipitation=round(sense.humidity,0)
        return round(precipitation,1)
    
    def humidity_to_wind(self):
        wind=(round(sense.pressure,0)-260)/20
        return round(wind,1)

    def read_sensor(self):
        self.t=round(sense.get_temperature(),0)
        self.precipitation=self.press_to_precipitation()
        self.wind=self.humidity_to_wind()		

    def insert_in_database(self):
        self.read_sensor()
        time_str=str(datetime.datetime.now().strftime("%H:%M %d.%m.%y"))
        data=[time_str,self.t,self.wind,self.precipitation]
        self.insert_data(data)


inside_data_table="sensehat_data"
outside_data_table="open_meteo__current_data"



#current weather table
create_current_outside_table=f'''CREATE TABLE IF NOT EXISTS {outside_data_table}(
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					timestamp TEXT NOT NULL,
					temperature REAL,
					humidity REAL,
					pressure REAL,
					wind_speed REAL);'''
			
insert_current_outside_query=f'''INSERT INTO {outside_data_table} (timestamp,temperature,humidity,pressure,wind_speed)
VALUES (?,?,?,?,?);
'''
current_read_query=f'''SELECT * FROM {outside_data_table} ORDER BY id DESC LIMIT 1'''

#sensehat table
create_sensehat_table=f'''CREATE TABLE IF NOT EXISTS {inside_data_table} (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				timestamp TEXT NOT NULL,
				temperature_in INTEGER,
				humidity_in INTEGER,
				pressure_in INTEGER);'''
				
sensehat_insert_query=f'''INSERT INTO {inside_data_table} (timestamp,temperature_in,humidity_in,pressure_in)
					VALUES (?,?,?,?);'''
sensehat_read_query=f'''SELECT * FROM {inside_data_table} ORDER BY id DESC LIMIT 1'''




if __name__=="__main__":
    last_time=time.time()
    inside_info=SenseHatInfo(inside_data_table,create_sensehat_table,sensehat_insert_query,sensehat_read_query)
    outside_info=CurrentWeather(outside_data_table,create_current_outside_table,insert_current_outside_query,current_read_query)
    forecast_weather=ForecastWeather()
    SimulationInside=SimInside()
    SimulationOutside=SimOutside()
        
    
    while True:
        current_time=time.time()
        if current_time-last_time>3:
            SimulationInside.insert_in_database()
            SimulationOutside.insert_in_database()
            #print(f"IN: {SimulationInside.read_data()}")
            #print(f"OUT:{SimulationOutside.read_data()}")	
            inside_info.insert_in_database()
            outside_info.insert_in_database()
            #print(inside_info.read_data())
            #print(outside_info.read_data())
            #forecast_weather.read_forecast()
            last_time=current_time
        print(forecast_weather.read_forecast())

	
	
	
	
	
	
	
	
	
	
	
	
