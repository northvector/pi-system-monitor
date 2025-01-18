import tkinter as tk
import requests
import math

# Change this line! use your system ip
OHM_SERVER_URL = "http://192.168.88.100:8085/data.json"

def checkData(data, Text, Children):
    try:
        for data in data['Children']:
            if (data['Text'] == Text):
                for data in data['Children']:
                    if (data['Text'] == Children):
                        return (data['Value'])
            else:
                result = (checkData(data, Text, Children))
                if (result):
                    return result
    except NameError:
        print("well, it WASN'T defined after all!")

class TemperatureMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Temperature Monitor")
        self.root.attributes('-fullscreen', True)  
        self.root.config(bg='black')
        self.canvas = tk.Canvas(self.root, width=480, height=320, bg='#000000')
        self.canvas.pack()

        self.update_data()  

    def fetch_temperatures(self):
        """Fetch temperature data from the OpenHardwareMonitor API."""
        try:
            response = requests.get(OHM_SERVER_URL, timeout=5)  
            response.raise_for_status()
            data = response.json()
            sensors = []

            
            cpu_temp = float(checkData(data, "Temperatures", "CPU Package").split('°C')[0]) if checkData(data, "Temperatures", "CPU Package") else None
            gpu_temp = float(checkData(data, "Temperatures", "GPU Core").split('°C')[0]) if checkData(data, "Temperatures", "GPU Core") else None
            cpu_load = float(checkData(data, "Load", "CPU Total").split('%')[0]) if checkData(data, "Load", "CPU Total") else None
            gpu_load = float(checkData(data, "Load", "GPU Core").split('%')[0]) if checkData(data, "Load", "GPU Core") else None
            gpu_vram_total = float(checkData(data, "Data", "GPU Memory Total").split('MB')[0]) if checkData(data, "Data", "GPU Memory Total") else None
            gpu_vram_used = float(checkData(data, "Data", "GPU Memory Used").split('MB')[0]) if checkData(data, "Data", "GPU Memory Used") else None
            gpu_vram_Free = float(checkData(data, "Data", "GPU Memory Free").split('MB')[0]) if checkData(data, "Data", "GPU Memory Free") else None

            RAM_load = float(checkData(data, "Load", "Memory").split('%')[0]) if checkData(data, "Load", "Memory") else None
            gpu_power = float(checkData(data, "Powers", "GPU Power").split('W')[0]) if checkData(data, "Powers", "GPU Power") else None
            disk_load = float(checkData(data, "Load", "Used Space").split('%')[0]) if checkData(data, "Load", "Used Space") else None
            gpu_fan_rpm = float(checkData(data, "Fans", "GPU").split('RPM')[0]) if checkData(data, "Fans", "GPU") else None
            used_memory = float(checkData(data, "Data", "Used Memory").split('GB')[0]) if checkData(data, "Data", "Used Memory") else None
            Available_memory = float(checkData(data, "Data", "Available Memory").split('GB')[0]) if checkData(data, "Data", "Available Memory") else None

            if gpu_temp is not None:
                sensors.append({"name": "GPU Temp", "value": gpu_temp,"display": "chart", "unit": "°C", "color": "green", "max": 100})
            if gpu_fan_rpm is not None:
                sensors.append({"name": "GPU Fan", "value": gpu_fan_rpm,"display": "chart", "unit": "RPM", "color": "green", "max": 4000})
            if gpu_vram_total is not None:
                sensors.append({"name": "GPU VRAM", "value": math.ceil(gpu_vram_used / gpu_vram_total * 100),"display": "chart", "unit": "%", "color": "green", "max": 100})
            if gpu_load is not None:
                sensors.append({"name": "GPU Load", "value": gpu_load,"display": "chart", "unit": "%", "color": "green", "max": 100})
            if gpu_power is not None:
                sensors.append({"name": "GPU Power", "value": gpu_power,"display": "chart", "unit": "W", "color": "orange", "max": 260})
            if cpu_load is not None:
                sensors.append({"name": "CPU Load", "value": cpu_load,"display": "chart",  "unit": "%", "color": "blue", "max": 100})
            if cpu_temp is not None:
                sensors.append({"name": "CPU Temp", "value": cpu_temp,"display": "chart", "unit": "°C", "color": "blue", "max": 100})
            if RAM_load is not None:
                sensors.append({"name": "RAM", "value": RAM_load,"display": "chart", "unit": "%", "color": "yellow", "max": 100})
            if used_memory is not None:
                sensors.append({"name": "Used Memory", "value": used_memory, "display": "text",  "unit": "GB", "color": "pink", "max": used_memory + Available_memory})
            if Available_memory is not None:
                sensors.append({"name": "Available Memory", "display": "text", "value": Available_memory, "unit": "GB", "color": "pink", "max": used_memory + Available_memory})
            if disk_load is not None:
                sensors.append({"name": "Disk" , "value": disk_load,"display": "chart" , "unit": "%", "color": "pink", "max": 100})
            return sensors

        except requests.exceptions.RequestException as e:
            print(f"Error fetching temperatures: {e}")
            return []  

    def draw_circle_progress(self, x, y, radius, value, max_value, filled_color, unfilled_color="black", width=10):
        """Draw a circular progress bar with smooth filling."""
        import math

        if max_value <= 0:
            raise ValueError("max_value must be greater than 0.")
        
        extent = (value / max_value) * 360
        self.canvas.create_arc(
            x - radius, y - radius, x + radius, y + radius,
            start=90, extent=-extent,
            style="arc",
            outline=filled_color, width=width
        )
        self.canvas.create_arc(
            x - radius, y - radius, x + radius, y + radius,
            start=90 - extent, extent=-(360 - extent),
            style="arc",
            outline=unfilled_color, width=width
        )

    # update reload the current page every 1 seconds
    def update_data(self):
        """Update the data on the GUI with fetched temperature data."""
        sensors = self.fetch_temperatures()
        sensors_per_page = 6
        if not sensors:
            self.canvas.delete("all")
            self.canvas.create_text(240, 160, text="No Data Available", font=('Quicksand', 24), fill='red')
            return

        total_sensors = len(sensors)
        total_pages = (total_sensors + sensors_per_page - 1) // sensors_per_page 

        if not hasattr(self, "current_page"):
            self.current_page = 0
        self.canvas.delete("all")
        start_index = self.current_page * sensors_per_page
        end_index = start_index + sensors_per_page

        page_sensors = sensors[start_index:end_index]

        for index, sensor in enumerate(page_sensors):
            y_position = 90 if index < 3 else 240
            x_position = 70 + (index % 3) * 160
            name = sensor["name"]
            value = sensor["value"] if sensor["value"] is not None else 0.0
            unit = sensor["unit"]
            display = sensor["display"]
            max_value = sensor["max"] if sensor["max"] is not None else 100
            color = sensor["color"] if sensor["color"] is not None else "white"

            if display == "chart":
                self.draw_circle_progress(x_position, y_position, 45, value, max_value, color, "#212121", 12)
                self.canvas.create_text(x_position, y_position - 70, text=name, font=('Quicksand', 17, "bold"), fill='white')
                self.canvas.create_text(x_position, y_position, text=f"{value} {unit}", font=('Quicksand', 15), fill='white', anchor="center")

            elif display == "text":
                self.canvas.create_text(x_position, y_position - 70, text=name, font=('Quicksand', 12, "bold"), fill='white')
                self.canvas.create_text(x_position, y_position - 40, text=f"{value} {unit}", font=('Quicksand', 15), fill='white', anchor="center")

        self.canvas.create_text(480/2 - 10, 310, text=f"Page {self.current_page + 1} / {total_pages}", font=('Quicksand', 10), fill='white')

        def change_page(direction):
            if direction == "next":
                self.current_page = (self.current_page + 1) % total_pages
            elif direction == "prev":
                self.current_page = (self.current_page - 1) % total_pages
            self.update_data()

        self.canvas.tag_bind("all", "<Button-1>", lambda event: change_page("next"))
        self.canvas.tag_bind("all", "<Button-3>", lambda event: change_page("prev"))
        self.root.after(2000, self.update_data)



root = tk.Tk()
app = TemperatureMonitorApp(root)
root.mainloop()
