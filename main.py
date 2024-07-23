import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from write_SQL import ForecastWeather,SenseHatInfo,CurrentWeather,SimInside,SimOutside
import numpy as np
#backgrounds and icons

width=900
height=600
weathericon_x,weathericon_y=120,90
top_clothes_x,top_clothes_y=60,60
upper_clothes_x,upper_clothes_y=60,60
lower_clothes_x,lower_clothes_y=60,60
bottom_clothes_x,bottom_clothes_y=60,60

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
current_read_query=f'''SELECT * FROM {outside_data_table} ORDER BY id DESC LIMIT 1'''


ForWea=ForecastWeather()
SenseHatInfo=SenseHatInfo(inside_data_table,create_sensehat_table,sensehat_insert_query,sensehat_read_query)
CurrWea=CurrentWeather(outside_data_table,create_current_outside_table,insert_current_outside_query,current_read_query)
SimulationInside=SimInside()
SimulationOutside=SimOutside()

#id_s,timestamp_s,temp_s,pressure_s,humidity_s=SenseHatInfo.read_data()


class MySmartHome():
    def __init__(self,root):
        
        #main window
        self.root = root
        self.root.title("My Smart Home")
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False,False)

        tab_width=int(width/3)
        style = ttk.Style()
        style.configure('TNotebook.Tab', padding=[10, 5], font=('TkDefaultFont', 25),bg="lightblue", width=tab_width)
        self.notebook=ttk.Notebook(self.root,style="TNotebook")
        
        self.tab1=tk.Frame(self.notebook)
        self.tab2=tk.Frame(self.notebook)
        self.tab3=tk.Frame(self.notebook)
        self.notebook.add(self.tab1,text="Home")
        self.notebook.add(self.tab2,text="Climate")
        self.notebook.add(self.tab3,text="Forecast")
        self.notebook.pack(expand=1,fill="both")
        self.data_index=2
        self.define_variables()
        self.setup_icons()
        self.setup_tab1()
        self.setup_tab2()
        self.setup_tab3()
        self.update_data()
        self.update_icons_tab1()

        
    def update_data(self):
        if True:
                #write new data in SQL
                SenseHatInfo.insert_in_database()
                CurrWea.insert_in_database()
                SimulationInside.insert_in_database()
                SimulationOutside.insert_in_database()
                #reading simulated data with emulator
                ID_in,timestamp_in,self.temp_in,self.humidity_in,self.aq_in=SimulationInside.read_data()
                ID_out,timestamp_out,self.temp_out,self.wind_out,self.precipitation_out=SimulationOutside.read_data()
                id_c,self.CW1_ts,self.CW2_t,self.CW_h,self.CW_p,self.wind_c=CurrWea.read_data()                  
                self.in_temp_var.set(self.temp_in)
                self.in_humidity_var.set(self.humidity_in)
                self.in_aq_var.set(self.aq_in)
                self.out_temp_var.set(self.temp_out)
                self.out_precipitation_var.set(self.precipitation_out)
                self.out_wind_var.set(self.wind_out) 
                #dodati air quality
                
                   
          
        #refresh and update weather data 
        self.update_icons_tab1()
        self.message_check()
        self.root.after(500,self.update_data)

    def define_variables(self):
        self.in_temp_var=tk.StringVar()
        self.in_humidity_var=tk.StringVar()
        self.in_pressure_var=tk.StringVar()
        self.in_settemp_var=tk.IntVar()
        self.in_settemp_var.set(20)
        self.message_var=tk.StringVar()
        self.out_temp_var=tk.StringVar()
        self.out_precipitation_var=tk.StringVar()
        self.out_pressure_var=tk.StringVar()
        self.out_air_quality_var=tk.StringVar()
        self.out_wind_var=tk.StringVar()
        self.in_aq_var=tk.StringVar()
        self.out_precipitation_var=tk.StringVar()
        self.warning_message=tk.StringVar()
        self.fan_speed=tk.IntVar()

    def update_icons_tab1(self):
        if float(self.out_temp_var.get()) >= 32:
            head_icon=self.sunny_hat_file
            torso_icon=self.t_shirt_file
            legs_icon=self.shorts_file
            feet_icon=self.sneakers_file        
        elif 32 > float(self.out_temp_var.get()) >= 26:
            head_icon=None
            torso_icon=self.t_shirt_file
            legs_icon=self.shorts_file
            feet_icon=self.sneakers_file
        elif 26 > float(self.out_temp_var.get()) >= 22:
            head_icon=None
            torso_icon=self.t_shirt_file
            legs_icon=self.longs_file
            feet_icon=self.sneakers_file
        elif 22 > float(self.out_temp_var.get()) >= 12:
            head_icon=None
            torso_icon=self.t_shirt_file # change to long sleeve or light jacket
            legs_icon=self.longs_file
            feet_icon=self.sneakers_file
        elif 12 > float(self.out_temp_var.get()) >= 0:
            head_icon=None
            torso_icon=self.jacket_file
            legs_icon=self.longs_file
            feet_icon=self.sneakers_file
        elif 0 > float(self.out_temp_var.get()):
            head_icon=self.wool_hat_file
            torso_icon=self.jacket_file
            legs_icon=self.longs_file
            feet_icon=self.boots_file


        if head_icon:
            self.tab1_canvas.itemconfig(self.clothes_icons["head"],image=head_icon)
            self.tab1_canvas.itemconfig(self.clothes_icons["head"],state="normal")
        else:
            self.tab1_canvas.itemconfig(self.clothes_icons["head"],state="hidden") 
        
        self.tab1_canvas.itemconfig(self.clothes_icons["upper_body"],image=torso_icon)
        self.tab1_canvas.itemconfig(self.clothes_icons["lower_body"],image=legs_icon)
        self.tab1_canvas.itemconfig(self.clothes_icons["feet"],image=feet_icon)
        
        if float(self.out_precipitation_var.get())<=20:
            main_weather_icon=self.sun_file
            self.tab1_canvas.itemconfig(self.clothes_icons["umbrella"],state="hidden")
        elif 20<float(self.out_precipitation_var.get())<=40:
            main_weather_icon=self.cloud_sun_file
            self.tab1_canvas.itemconfig(self.clothes_icons["umbrella"],state="hidden")
        if 40<float(self.out_precipitation_var.get())<=60:

            main_weather_icon=self.cloud_file
            self.tab1_canvas.itemconfig(self.clothes_icons["umbrella"],state="normal") 
        if 60<float(self.out_precipitation_var.get())<=100:
            if float(self.out_temp_var.get())<0:
                main_weather_icon=self.snow_file
            else:
                main_weather_icon=self.cloud_rain_file

            
        self.tab1_canvas.itemconfig(self.weather_icons["main_icon"],image=main_weather_icon)
            
        #strong wind icon
        if float(self.out_wind_var.get())>15:
            self.tab1_canvas.itemconfig(self.weather_icons["wind_icon"],state="normal")
        elif float(self.out_wind_var.get())>30:
            self.tab1_canvas.itemconfig(self.weather_icons["wind_icon"],state="normal") 
            self.warning_message.set("Upozorenje: jak vjetar")                            
        else:
            self.tab1_canvas.itemconfig(self.weather_icons["wind_icon"],state="hidden")
        #high temperature icon
        if float(self.out_temp_var.get())>30:
            self.tab1_canvas.itemconfig(self.weather_icons["temperature_icon"],image=self.high_temp_file)                
            self.tab1_canvas.itemconfig(self.weather_icons["temperature_icon"],state="normal")
            self.warning_message.set("Upozorenje: visoke temperature")            
        elif float(self.out_temp_var.get())<0:
            self.tab1_canvas.itemconfig(self.weather_icons["temperature_icon"],image=self.low_temp_file)
            self.tab1_canvas.itemconfig(self.weather_icons["temperature_icon"],state="normal")
            self.warning_message.set("Upozorenje: Moguća poledica")
        else:
            self.tab1_canvas.itemconfig(self.weather_icons["temperature_icon"],state="hidden")
            self.warning_message.set("")
        #update numerical values in tab1 
        self.tab1_canvas.itemconfig(self.tab1_outer_temp,text=self.out_temp_var.get())
        self.tab1_canvas.itemconfig(self.tab1_inner_temp,text=self.in_temp_var.get())
        self.tab1_canvas.itemconfig(self.tab1_wind,text=self.out_wind_var.get())
        self.tab1_canvas.itemconfig(self.tab1_message_label,text=self.warning_message.get())



    def setup_tab1(self):
        #bacis icons and background
        self.tab1_canvas=tk.Canvas(self.tab1,width=900,height=600)
        self.tab1_canvas.create_image(0,0,anchor=tk.NW,image=self.bkg_file)
        self.tab1_canvas.create_image(300,150,anchor=tk.NW,image=self.backgroundhouse_file) #house icon
        #dynamic weather icons
        self.weather_icons={
        "main_icon":self.tab1_canvas.create_image(35,50,anchor=tk.NW,image=self.sun_file),
        "wind_icon":self.tab1_canvas.create_image(125,90,anchor=tk.NW,image=self.strong_wind_file),
        "temperature_icon":self.tab1_canvas.create_image(125,50,anchor=tk.NW,image=self.high_temp_file)}
        #dynamic clothing icons
        self.clothes_icons={
        "head" : self.tab1_canvas.create_image(width-100,height-bottom_clothes_y-lower_clothes_y-upper_clothes_y-top_clothes_y-50,anchor=tk.NW,image=self.wool_hat_file),
        "upper_body": self.tab1_canvas.create_image(width-100,height-bottom_clothes_y-lower_clothes_y-upper_clothes_y-50,anchor=tk.NW,image=self.t_shirt_file),
        "lower_body": self.tab1_canvas.create_image(width-100,height-bottom_clothes_y-lower_clothes_y-50,anchor=tk.NW,image=self.longs_file),
        "feet": self.tab1_canvas.create_image(width-100,height-bottom_clothes_y-50,anchor=tk.NW,image=self.sneakers_file),
        "umbrella": self.tab1_canvas.create_image(width-170,height-bottom_clothes_y-lower_clothes_y-upper_clothes_y-top_clothes_y-20,anchor=tk.NW,image=self.umbrella_file)}
        #dynamic texts
        self.tab1_outer_temp=self.tab1_canvas.create_text(250,20,text=f"{self.out_temp_var.get()}°C",font=("Segoe UI",25),fill="white")
        self.tab1_outer_temp_label=self.tab1_canvas.create_text(140,20,text="Vanjska\ntemperatura",font=("Segoe UI",15),fill="white")
        self.tab1_inner_temp=self.tab1_canvas.create_text(390,465,text=f"{self.in_temp_var.get()}C",font=("Segoe UI",25))
        self.tab1_inner_temp_label=self.tab1_canvas.create_text(390,430,text="Unutarnja\ntemperatura",font=("Segoe UI",15))        
        self.tab1_wind=self.tab1_canvas.create_text(140,495,text=f"{self.out_wind_var.get()} ms",font=("Segoe UI",15),fill="white")
        self.tab1_wind_label=self.tab1_canvas.create_text(140,460,text="Vjetar",font=("Segoe UI",15),fill="white")        
        self.tab1_message_label=self.tab1_canvas.create_text(width-300,50,text=self.warning_message,font=("Segoe UI",15,"bold"),fill="red")
        self.tab1_canvas.pack()

        
    def setup_tab2(self):

        #simulacija temperature unutra sa sensehatom
        #odabir unutarnje temperature sa tipkovnicom
        #simulacija vanjske temperature 
        #paljenje klime
        self.out_panel=tk.Frame(self.tab2,width=300,height=600,bg="lightblue",relief=tk.RAISED, borderwidth=1)
        self.in_panel=tk.Frame(self.tab2,width=600,height=200,bg="lightblue",relief=tk.RAISED, borderwidth=1)
        self.device_panel=tk.Frame(self.tab2,width=600,height=400,relief=tk.RAISED, borderwidth=1)

        self.in_panel.grid_columnconfigure((0,1),weight=1,uniform="column")

        self.heating_panel=tk.Frame(self.device_panel,width=600,height=400,bg="lightblue",relief=tk.RAISED, borderwidth=1)
        self.ac_panel=tk.Frame(self.device_panel,width=600,height=400,bg="lightblue",relief=tk.RAISED, borderwidth=1)
        self.out_panel.grid_propagate(False)
        self.in_panel.grid_propagate(False)
        self.device_panel.grid_propagate(False)
        self.out_panel.grid(row=0,column=0,rowspan=2,sticky="ns")
        self.in_panel.grid(row=0,column=1,sticky="ns")
        self.device_panel.grid(row=1,column=1,sticky="ns")
        self.ac_panel_f()
        self.heating_panel_f()
        
        
        #inside panel
        self.in_temp_label=tk.Label(self.in_panel,text="Unutarnja temperatura",bg="lightblue",font=("Segoe UI",16))
        self.in_temp=tk.Label(self.in_panel,textvariable=self.in_temp_var,bg="lightblue",font=("Segoe UI",16))
        self.in_pressure_label=tk.Label(self.in_panel,text="unutarnji tlak zraka",bg="lightblue",font=("Segoe UI",16))
        self.in_pressure=tk.Label(self.in_panel,textvariable=self.in_pressure_var,bg="lightblue",font=("Segoe UI",16))
        self.in_humidity_label=tk.Label(self.in_panel,text="Vlaga zraka",bg="lightblue",font=("Segoe UI",16))
        self.in_humidity=tk.Label(self.in_panel,textvariable=self.in_humidity_var,bg="lightblue",font=("Segoe UI",16))
        self.in_aq_label=tk.Label(self.in_panel,text="Kvaliteta zraka",bg="lightblue",font=("Segoe UI",16))
        self.in_aq=tk.Label(self.in_panel,textvariable=self.in_aq_var,bg="lightblue",font=("Segoe UI",16))
        self.reccomendation_label=tk.Label(self.in_panel,textvariable=self.message_var,bg="lightblue",font=("Segoe UI",16))
        self.ac_button=tk.Button(self.in_panel,text="KLIMA",relief=tk.RAISED,command=self.ac_panel_f,bg="#4287f5",padx=5,pady=5)
        self.heating_button=tk.Button(self.in_panel,text="GRIJANJE",relief=tk.RAISED,command=self.heating_panel_f,bg="#4287f5",padx=5,pady=5)
        
        #placing in in_panel
        self.in_temp_label.grid(row=1,column=0)
        self.in_humidity_label.grid(row=2,column=0)
        self.in_pressure_label.grid(row=3,column=0)
        self.in_aq_label.grid(row=4,column=0)
        self.in_temp.grid(row=1,column=1)
        self.in_humidity.grid(row=2,column=1)
        self.in_pressure.grid(row=3,column=1)
        self.in_aq.grid(row=4,column=1)
        self.reccomendation_label.grid(row=5,column=0,columnspan=2)
        self.ac_button.grid(row=6,column=0,sticky="ew")
        self.heating_button.grid(row=6,column=1,sticky="ew")  

        #outside panel
        self.out_temp=tk.Label(self.out_panel,textvariable=self.out_temp_var,bg="lightblue",font=("Segoe UI",16))
        self.out_humidity=tk.Label(self.out_panel,textvariable=self.out_precipitation_var,bg="lightblue",font=("Segoe UI",16))
        self.out_wind=tk.Label(self.out_panel,textvariable=self.out_wind_var,bg="lightblue",font=("Segoe UI",16))
        self.out_airquality=tk.Label(self.out_panel,textvariable="40",bg="lightblue",font=("Segoe UI",16))
        self.out_temp_label=tk.Label(self.out_panel,text="Temperatura",bg="lightblue",font=("Segoe UI",16))
        self.out_airquality_label=tk.Label(self.out_panel,text="Kvaliteta zraka",bg="lightblue",font=("Segoe UI",16))
        self.out_humidity_label=tk.Label(self.out_panel,text="Vlaga zraka",bg="lightblue",font=("Segoe UI",16))
        self.out_wind_label=tk.Label(self.out_panel,text="Vjetar",bg="lightblue",font=("Segoe UI",16))
        self.out_temp_label.grid(row=0,column=0)
        self.out_temp.grid(row=1,column=0)
        self.out_humidity_label.grid(row=2,column=0)
        self.out_humidity.grid(row=3,column=0)
        self.out_wind_label.grid(row=4,column=0)
        self.out_wind.grid(row=5,column=0)
        self.out_airquality_label.grid(row=6,column=0)
        self.out_airquality.grid(row=7,column=0)

        #heating panel
        
        self.heating_left=tk.Frame(self.heating_panel,bg="lightblue",width=300,height=360)
        self.heating_right=tk.Frame(self.heating_panel,bg="lightblue",width=300,height=360)
        self.heating_left.grid(row=0,column=0)
        self.heating_right.grid(row=0,column=1)
        self.heating_panel.grid_propagate(False)
        
        self.heating_button_up=tk.Button(self.heating_right,text="+",bg="#4287f5",font=("Segoe UI",25,"bold"),width=5,height=3,command=self.heat_temp_up)
        self.heating_button_down=tk.Button(self.heating_right,text="-",bg="#4287f5",font=("Segoe UI",25,"bold"),width=5,height=3,command=self.heat_temp_down)
        self.heating_label=tk.Label(self.heating_left,textvariable=self.in_settemp_var,bg="lightblue",font=("Segoe UI",25,"bold"),width=5,height=3)
        self.heating_on=tk.Button(self.heating_left,text="ON",fg="green",bg="#4287f5",font=("Segoe UI",18,"bold"),width=5,height=2,command=self.switch_heat_on)
        self.heating_off=tk.Button(self.heating_left,text="OFF",fg="red",bg="#4287f5",font=("Segoe UI",18,"bold"),width=5,height=2,command=self.switch_heat_off)
        self.heating_button_up.pack()
        self.heating_button_down.pack()
        self.heating_on.grid(row=0,column=0)
        self.heating_off.grid(row=0,column=1)
        self.heating_label.grid(row=1,column=0,columnspan=2,padx=30,pady=30)
        #ac panel
        self.ac_panel.grid_propagate(False)
        self.ac_panel.grid_columnconfigure((0,1,2,3,4),weight=1,uniform="column")
        self.slider_value_var = tk.IntVar()
        self.slider_value_var.set(22)
        self.ac_temp_label = tk.Label(self.ac_panel, textvariable=self.slider_value_var,bg="lightblue", font=("Segoe UI", 20))
        self.ac_off=tk.Button(self.ac_panel,text="OFF",fg="red",bg="#4287f5",font=("Segoe UI",18,"bold"),width=5,height=2,command=self.switch_ac_off)
        self.ac_on=tk.Button(self.ac_panel,text="ON",fg="green",bg="#4287f5",font=("Segoe UI",18,"bold"),width=5,height=2,command=self.switch_ac_on)

        self.slider = tk.Scale(self.ac_panel, from_=16, to=32, orient=tk.HORIZONTAL,bg="lightblue", variable=self.slider_value_var, length=150)
        self.fan_speed_1=tk.Radiobutton(self.ac_panel,text="HIGH",bg="lightblue",variable=self.fan_speed,value=1)
        self.fan_speed_2=tk.Radiobutton(self.ac_panel,text="MEDIUM",bg="lightblue",variable=self.fan_speed,value=2)
        self.fan_speed_3=tk.Radiobutton(self.ac_panel,text="LOW",bg="lightblue",variable=self.fan_speed,value=3)
        self.fan_label=tk.Label(self.ac_panel,text="Fan speed",bg="lightblue", font=("Segoe UI", 18))
        self.ac_temp=tk.Label(self.ac_panel,text="Set temp",bg="lightblue", font=("Segoe UI", 18))
        self.ac_off.grid(row=0,column=1, pady=5, padx=5)
        self.ac_on.grid(row=0,column=0, pady=5, padx=5)
        self.ac_temp.grid(row=0, column=3, columnspan=2, pady=5, padx=5)
        self.ac_temp_label.grid(row=1, column=3, columnspan=2, pady=5, padx=5)
        self.slider.grid(row=2, column=2, columnspan=3, pady=5, padx=5)
        self.fan_label.grid(row=3,column=0,columnspan=2)
        self.fan_speed_1.grid(row=3,column=2)
        self.fan_speed_2.grid(row=3,column=3)
        self.fan_speed_3.grid(row=3,column=4)
        self.switch_ac_off()
        self.switch_heat_off()

    def message_check(self):
        if self.out_air_quality_var.get()<self.in_aq_var.get():
                self.message_var.set("prozračite, vani je kvalitetniji zrak")
        else:
                self.message_var.set("zatvorite prozore, vani je zagađeniji zrak")
        
    def ac_panel_f(self):
        self.heating_panel.pack_forget()
        self.ac_panel.pack()
        #self.ac_button.config(relief=tk.SUNKEN)
        #self.heating_button.config(relief=tk.RAISED)        


    def heating_panel_f(self):
        self.ac_panel.pack_forget()
        self.heating_panel.pack()
        #s#elf.ac_button.config(relief=tk.RAISED)
        #self.heating_button.config(relief=tk.SUNKEN)  

    def switch_heat_off(self):
        self.heating_on.config(state="normal")  
        self.heating_button_down.config(state="disabled")
        self.heating_button_up.config(state="disabled")
        self.heating_label.config(state="disabled")
        self.heating_off.config(state="disabled")

    def switch_heat_on(self):
        self.switch_ac_off()
        self.heating_off.config(state="normal") 
        self.heating_button_down.config(state="normal")
        self.heating_button_up.config(state="normal")
        self.heating_label.config(state="normal") 
        self.heating_on.config(state="disabled")       
        
    def heat_temp_up(self):
        self.in_settemp_var.set(self.in_settemp_var.get()+1)
        if self.in_settemp_var.get()>28:
            self.in_settemp_var.set(28)  
              
    def heat_temp_down(self):
        self.in_settemp_var.set(self.in_settemp_var.get()-1)        
        if self.in_settemp_var.get()<12:
            self.in_settemp_var.set(12)        
            
    def switch_ac_off(self):
            self.ac_off.config(state="disabled")
            self.ac_on.config(state="normal")
            self.fan_speed_1.config(state="disabled")
            self.fan_speed_2.config(state="disabled")
            self.fan_speed_3.config(state="disabled")
            self.fan_label.config(state="disabled") 
            self.slider.config(state="disabled")
            self.ac_temp.config(state="disabled")
            self.ac_temp_label.config(state="disabled")

    def switch_ac_on(self):
            self.switch_heat_off()
            self.ac_off.config(state="normal")
            self.ac_on.config(state="disabled")
            self.fan_speed_1.config(state="normal")
            self.fan_speed_2.config(state="normal")
            self.fan_speed_3.config(state="normal")
            self.fan_label.config(state="normal") 
            self.slider.config(state="normal")
            self.ac_temp.config(state="normal")
            self.ac_temp_label.config(state="normal")

    def setup_tab3(self):
        #setting up canvas
        self.t_time=1
        self.t_max=66
        self.update_forecast()
        self.forecast_data=ForWea.read_forecast()
        self.ind=[]
        for i in self.forecast_data.keys():
            if i=="Time":
                pass
            else:
                self.ind.append(i)
        self.fig,self.ax1=plt.subplots(figsize=(10,4))
        self.plot_canvas = FigureCanvasTkAgg(self.fig, master=self.tab3)
        self.plot_canvas.get_tk_widget().pack(side=tk.TOP, pady=20)
        self.ax1.clear()
        self.ax1.plot(self.forecast_data["Time"][self.t_time:self.t_time+5],self.forecast_data[self.ind[self.data_index]][self.t_time:self.t_time+5])
        self.ax1.set_title(f"{self.ind[self.data_index]}")
        self.update_plot()
        self.tab3_label=tk.Label(self.tab3,text= "arrows move graphs")
        self.tab3_left_b=tk.Button(self.tab3,text="vrijeme -",command=self.on_left_press)
        self.tab3_right_b=tk.Button(self.tab3,text="vrijeme +",command=self.on_right_press)
        self.tab3_up_b=tk.Button(self.tab3,text="podatak +",command=self.on_up_press)
        self.tab3_down_b=tk.Button(self.tab3,text="podatak -",command=self.on_down_press)        
        self.tab3_left_b.pack(side="left")
        self.tab3_down_b.pack()
        self.tab3_up_b.pack()
        self.tab3_right_b.pack(side="right")
        self.plot_canvas.draw()

    def update_forecast(self):
        ForWea.weather_values()
        self.root.after(600000,self.update_forecast)
            
            
    def on_left_press(self):
        print("left")
        self.t_time-=1
        if self.t_time<1:
                1
        self.update_plot()
        
    def on_right_press(self):
        print("right")
        self.t_time+=1
        if self.t_time>self.t_max:
                selt.t_time=self.t_max
        self.update_plot()
                
        
    def on_up_press(self):
        self.data_index+=1
        if self.data_index >=len(self.forecast_data)-1:
            self.data_index = 0 
        self.update_plot()

    def on_down_press(self):
        self.data_index-=1
        if self.data_index < 0:
            self.data_index = len(self.forecast_data)-2      
        self.update_plot()

    def update_plot(self):
        print("updating plot")
        self.ax1.clear()

        self.ax1.plot(self.forecast_data["Time"][self.t_time:self.t_time+5],self.forecast_data[self.ind[self.data_index]][self.t_time:self.t_time+5])
        self.ax1.set_title(f"{self.ind[self.data_index]}")
        self.ax1.grid()
        self.plot_canvas.draw()       

    def setup_icons(self):

        #file paths
        #weather icons
        self.bkg_jpg = Image.open(os.path.join("weather_icons","bkg.jpg"))
        self.backgroundhouse_png = Image.open(os.path.join("icons","backgroundhouse.png"))
        self.sun_png = Image.open(os.path.join("weather_icons","sunny.png"))
        self.cloud_png = Image.open(os.path.join("weather_icons","cloudy.png"))
        self.sun_rain_png = Image.open(os.path.join("weather_icons","sunny_rain.png"))
        self.cloud_sun_png = Image.open(os.path.join("weather_icons","cloud_sun.png"))
        self.cloud_rain_png = Image.open(os.path.join("weather_icons","cloud_rain.png"))
        self.snow_png = Image.open(os.path.join("weather_icons","snow.png"))
        self.strong_wind_png = Image.open(os.path.join("weather_icons","strong_wind.png"))
        self.high_temp_png = Image.open(os.path.join("weather_icons","extreme_high_temp.png"))
        self.cold_temp_png = Image.open(os.path.join("weather_icons","extreme_cold.png"))
        self.low_temp_png = Image.open(os.path.join("weather_icons","extreme_high_temp.png"))
        self.shorts_png = Image.open(os.path.join("icons","shorts.png"))
        self.longs_png = Image.open(os.path.join("icons","longs.png"))
        self.t_shirt_png = Image.open(os.path.join("icons","t-shirt.png"))
        self.jacket_png = Image.open(os.path.join("icons","jacket.png"))
        self.fat_jacket_png = Image.open(os.path.join("icons","jacket.png"))
        self.sunny_hat_png = Image.open(os.path.join("icons","sun_hat.jpg"))
        self.wool_hat_png = Image.open(os.path.join("icons","woolhat.png"))
        self.sneakers_png = Image.open(os.path.join("icons","sneakers.png"))
        self.boots_png = Image.open(os.path.join("icons","boots.png"))
        self.umbrella_png = Image.open(os.path.join("icons","umbrella.png"))
        #resizing images
        self.bkg_jpg = self.bkg_jpg.resize((900,600),Image.LANCZOS)
        self.backgroundhouse_png = self.backgroundhouse_png.resize((400,400),Image.LANCZOS)
        self.backgroundhouse_png = self.backgroundhouse_png.convert("RGBA")
        self.sun_png = self.sun_png.resize((weathericon_x,weathericon_y),Image.LANCZOS)
        self.sun_png = self.sun_png.convert("RGBA")
        self.sun_rain_png = self.sun_rain_png.resize((weathericon_x,weathericon_y),Image.LANCZOS)
        self.sun_rain_png = self.sun_rain_png.convert("RGBA")
        self.cloud_png = self.cloud_png.resize((weathericon_x,weathericon_y),Image.LANCZOS)
        self.cloud_png = self.cloud_png.convert("RGBA")
        self.cloud_rain_png = self.cloud_rain_png.resize((weathericon_x,weathericon_y),Image.LANCZOS)
        self.cloud_rain_png = self.cloud_rain_png.convert("RGBA")
        self.cloud_sun_png = self.cloud_sun_png.resize((weathericon_x,weathericon_y),Image.LANCZOS)
        self.cloud_sun_png = self.cloud_sun_png.convert("RGBA")
        self.snow_png = self.snow_png.resize((weathericon_x,weathericon_y),Image.LANCZOS)
        self.snow_png = self.snow_png.convert("RGBA")
        self.strong_wind_png = self.strong_wind_png.resize((90,80),Image.LANCZOS)
        self.strong_wind_png = self.strong_wind_png.convert("RGBA")
        self.high_temp_png = self.high_temp_png.resize((25,40),Image.LANCZOS)
        self.high_temp_png = self.high_temp_png.convert("RGBA")     
        self.cold_temp_png=self.cold_temp_png.resize((25,40),Image.LANCZOS)
        self.cold_temp_png=self.cold_temp_png.convert("RGBA") 
        
        self.shorts_png = self.shorts_png.resize((lower_clothes_x,lower_clothes_y),Image.LANCZOS)
        self.shorts_png = self.shorts_png.convert("RGBA")
        self.longs_png = self.longs_png.resize((lower_clothes_x,lower_clothes_y),Image.LANCZOS)
        self.longs_png = self.longs_png.convert("RGBA")
        self.t_shirt_png = self.t_shirt_png.resize((upper_clothes_x,upper_clothes_y),Image.LANCZOS)
        self.t_shirt_png = self.t_shirt_png.convert("RGBA")
        self.jacket_png = self.jacket_png.resize((upper_clothes_x,upper_clothes_y),Image.LANCZOS)
        self.jacket_png = self.jacket_png.convert("RGBA")
        self.sunny_hat_png = self.sunny_hat_png.resize((top_clothes_x,top_clothes_y),Image.LANCZOS)
        self.sunny_hat_png = self.sunny_hat_png.convert("RGBA")
        self.wool_hat_png = self.wool_hat_png.resize((top_clothes_x,top_clothes_y),Image.LANCZOS)
        self.wool_hat_png = self.wool_hat_png.convert("RGBA")
        self.sneakers_png = self.sneakers_png.resize((bottom_clothes_x,bottom_clothes_y),Image.LANCZOS)
        self.sneakers_png = self.sneakers_png.convert("RGBA")
        self.boots_png = self.boots_png.resize((bottom_clothes_x,bottom_clothes_y),Image.LANCZOS)
        self.boots_png = self.boots_png.convert("RGBA")
        self.umbrella_png = self.umbrella_png.resize((80,80),Image.LANCZOS)
        self.umbrella_png = self.umbrella_png.convert("RGBA")
        #importing to Tk     
        self.bkg_file = ImageTk.PhotoImage(self.bkg_jpg)
        self.backgroundhouse_file = ImageTk.PhotoImage(self.backgroundhouse_png)
        self.sun_file = ImageTk.PhotoImage(self.sun_png)
        self.sun_rain_file = ImageTk.PhotoImage(self.sun_rain_png)
        self.cloud_sun_file=ImageTk.PhotoImage(self.cloud_sun_png)
        self.cloud_file = ImageTk.PhotoImage(self.cloud_png)
        self.cloud_rain_file = ImageTk.PhotoImage(self.cloud_rain_png)
        self.snow_file = ImageTk.PhotoImage(self.snow_png)
        self.high_temp_file = ImageTk.PhotoImage(self.high_temp_png)
        self.low_temp_file = ImageTk.PhotoImage(self.cold_temp_png)
        self.strong_wind_file = ImageTk.PhotoImage(self.strong_wind_png)
        self.shorts_file = ImageTk.PhotoImage(self.shorts_png)
        self.longs_file = ImageTk.PhotoImage(self.longs_png)
        self.t_shirt_file = ImageTk.PhotoImage(self.t_shirt_png)
        self.jacket_file = ImageTk.PhotoImage(self.jacket_png)
        self.fat_jacket_file = ImageTk.PhotoImage(self.fat_jacket_png)
        self.sunny_hat_file = ImageTk.PhotoImage(self.sunny_hat_png)
        self.wool_hat_file = ImageTk.PhotoImage(self.wool_hat_png)
        self.sneakers_file = ImageTk.PhotoImage(self.sneakers_png)
        self.boots_file = ImageTk.PhotoImage(self.boots_png)
        self.umbrella_file = ImageTk.PhotoImage(self.umbrella_png)


if __name__=="__main__":
        root=tk.Tk()
        app=MySmartHome(root)
        root.mainloop()


















































