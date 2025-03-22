import csv
import random
import decimal


normal_params = {
    'rotation_speed': 10000,  # RPM
    'vibration': 2.0,         # mm/s
    'temperature': 75.0,      # °C
    'pressure': 550.0,        # Pa
    'flow_rate': 70.0,        # g/min
    'voltage': 380.0,         # V
    'current': 10.0           # A
}
all_data = []
for i in range(10000):
    rotation_speed = normal_params['rotation_speed'] + float(decimal.Decimal(random.randrange(-1000, 1000))/1)
    vibration = normal_params['vibration'] + float(decimal.Decimal(random.randrange(-10, 10))/100)
    temperature = normal_params['temperature'] + float(decimal.Decimal(random.randrange(-10, 10))/100)
    pressure = normal_params['pressure'] + float(decimal.Decimal(random.randrange(-10, 10))/100)
    flow_rate = normal_params['flow_rate'] + float(decimal.Decimal(random.randrange(-10, 10))/100)
    voltage = normal_params['voltage'] + float(decimal.Decimal(random.randrange(-10, 10))/100)
    current = normal_params['current'] + float(decimal.Decimal(random.randrange(-10, 10))/100)
    is_normal = True
    if random.randint(1, 10) == 10:
        if random.randint(1, 2) == 1:
            rotation_speed = rotation_speed + float(decimal.Decimal(random.randrange(-10000, -1000))/1)
            vibration = vibration + float(decimal.Decimal(random.randrange(-100, -10))/100)
            temperature = temperature + float(decimal.Decimal(random.randrange(-10, -5))/100)
            pressure = pressure + float(decimal.Decimal(random.randrange(-10, -5))/100)
            flow_rate = flow_rate + float(decimal.Decimal(random.randrange(-10, -5))/100)
            voltage = voltage + float(decimal.Decimal(random.randrange(-10, -5))/100)
            current = current + float(decimal.Decimal(random.randrange(-10, -5))/100)
        else:
            rotation_speed = rotation_speed + float(decimal.Decimal(random.randrange(1000, 10000))/1)
            vibration = vibration + float(decimal.Decimal(random.randrange(10, 100))/100)
            temperature = temperature + float(decimal.Decimal(random.randrange(5, 10))/100)
            pressure = pressure + float(decimal.Decimal(random.randrange(5, 10))/100)
            flow_rate = flow_rate + float(decimal.Decimal(random.randrange(5, 10))/100)
            voltage = voltage + float(decimal.Decimal(random.randrange(5, 10))/100)
            current = current + float(decimal.Decimal(random.randrange(5, 10))/100)
        is_normal = False
    # make this into csv format
    all_data.append([rotation_speed, vibration, temperature, pressure, flow_rate, voltage, current, is_normal])

with open('data.csv', "w") as f:
    writer = csv.writer(f)
    writer.writerow("rotation_speed,vibration,temperature,pressure,flow_rate,voltage,current,is_normal".split(","))
    writer.writerows(all_data)
