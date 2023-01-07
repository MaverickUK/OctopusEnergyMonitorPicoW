from wifi_connect import *
import urequests as requests
import ubinascii
import json
import math

# https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/examples/gfx_pack/button_test.py
import time
from gfx_pack import GfxPack, SWITCH_A, SWITCH_B, SWITCH_C, SWITCH_D, SWITCH_E

# Graphics setup
gp = GfxPack()
display = gp.display
WIDTH, HEIGHT = display.get_bounds()
display.set_backlight(0.5)  # White component of the backlight

# sets up a handy function we can call to clear the screen
def clear():
    display.set_pen(0)
    display.set_font("bitmap8")    
    display.clear()
    display.set_pen(15)

# Show splash screen
clear()
display.set_font("bitmap14_outline")
display.text('Octopus Energy monitor', 0, 0, WIDTH, 0)
display.set_font("bitmap6")
display.text('By Peter Bridger', 0, HEIGHT - 10, WIDTH, 0)
display.update()
time.sleep(2)
clear()

# Connect to wifi
wifi_connect()

   
def get_consumption_values( type, meter_number, serial, group_by, limit ):
    if type == 'e':
        type_component = 'electricity-meter-points'
    elif type == 'g':
        type_component = 'gas-meter-points'

    url = 'https://api.octopus.energy/v1/' + type_component + '/' + meter_number + '/meters/' + serial + '/consumption/?group_by=' + group_by

    print('Calling Octopus API for ' + type + ' by ' + group_by)
    print(url)

    # Keep retrying HTTP call
    headers = { 'authorization': secrets['auth_header'] }
    success = False
    while not success:
        try:
            request = requests.get(url, headers=headers, timeout=10) # Seconds
            data = json.loads(request.content)
            request.close()
            success = True
        except Exception as e:
            time.sleep(5)
            print('Retrying')
    
    i = 0
    values = []
    for result in data['results']:
        # Add to start of list (Ensure oldest readings are first)
        values.insert(0, (result['consumption'], result['interval_start']))
    
        i += 1
        if i >= limit:
            break
    
    return values # Older readings first


def draw_chart(values, y_min, y_max, bar_width, bar_offset, colour = 15):
    flip_mode = y_min > (HEIGHT / 2) # If true, drawing bars at bottom of screen
    
    # Determine max consumption value
    max_consumption = 0
   
    for value in values:
        if value[0] > max_consumption:
            max_consumption = value[0]
            
    max_consumption = round(max_consumption)
       
    scale_divider = max_consumption / (y_max - y_min)
    
    # Vertical scale
    line_max = y_min
    line_half = math.floor((y_max - y_min) / 2) + y_min
    display.set_pen(5)
    display.line(0, line_max, WIDTH, line_max ) # Max limit
    # display.set_pen(10)
    # display.line(0, line_half, WIDTH, line_half ) # Half
    
    max_label = str(max_consumption)
    label_width = display.measure_text(max_label, 1, 0)
     
    max_label_y = y_min + 2
    if flip_mode:
        max_label_y -= 10
    
    display.set_pen(15) # Black
    display.text(max_label, WIDTH - label_width - 4, max_label_y, scale=1)
    
    # Mode specific settings
    settings = get_settings()
    bar_spacing = settings['bar_spacing']
    bar_width = settings['bar_width']    
    
    # Bars
    i = 0
    display.set_pen(colour)
    for value in values:    
        scaled_consumption = math.floor(value[0] / scale_divider)
    
        # TODO: Use display.rectangle(x, y, w, h)
    
        for w in range(bar_width):
            x = (i * bar_spacing) + w + bar_offset 
            display.line( x, y_max - scaled_consumption, x, y_max)         
    
        i += 1
        
def format_datetime(date, index):
    datetime = date.split('T') # Date & time
    date_components = datetime[0].split('-')
    return date_components[index]

def display_consumption(group_by):
    clear()
    # Draw in PicoGraphics frame buffer
    display.text("Loading consumption by " + group_by + "...", 0, 0, WIDTH, 0)
    display.update() # Render
    
    # Mode specific settings
    settings = get_settings()
    print(settings)
    bar_spacing = settings['bar_spacing']
    bar_width = settings['bar_width']
    max_values = settings['max_values']
    label_index = settings['label_index']
    
    # Load data
    elec_values = get_consumption_values('e', secrets['mpan'], secrets['elec_serial'], group_by,  max_values)
    gas_values = get_consumption_values('g', secrets['mprn'], secrets['gas_serial'], group_by, max_values)

    clear()

    # Vertical line and dates
    display.line(0, 32, 128, 32) 
    for i in range(max_values):
        display.line((i * bar_spacing), 31, (i * bar_spacing), 34)
        display.text(format_datetime(elec_values[i][1], label_index), (i * bar_spacing) + bar_x_offset, 0, scale=1 )

    draw_chart(elec_values, energy_y_min, energy_y_max, bar_width, bar_x_offset)
    draw_chart(gas_values, gas_y_min, gas_y_max, bar_width, bar_x_offset, 10)

    # Labels
    display.set_pen(15) # Black
    label_width = display.measure_text("G", 1, 0)
    display.text("E", WIDTH - label_width, 0, scale=1)
    display.text("G", WIDTH - label_width, HEIGHT - (label_width * 2), scale=1)

    display.update() # Render
    
def display_about():
    clear()
    display.set_font("bitmap6")
    display.text('Account num: ' + secrets['account_number'], 0, 0, scale = 1)
    display.text('MPAN: ' + secrets['mpan'], 0, 10, scale = 1)
    display.text('MPRN: ' + secrets['mprn'], 0, 20, scale = 1)
    display.text('E serial: ' + secrets['elec_serial'], 0, 30, scale = 1)
    display.text('G serial: ' + secrets['gas_serial'], 0, 40, scale = 1)
    display.update()
    
def change_mode(new_mode):
    print('Changing mode to ' + new_mode )
    clear()
    global mode
    mode = new_mode
    display_consumption(mode)
    
def get_settings():
    print('Getting settings for ' + mode )
    if mode == 'day':
        return day_settings
    elif mode == 'week':
        return week_settings
    elif mode == 'month':
        return month_settings
    elif mode == 'quarter':
        return quarter_settings    

# Grouping specific 
day_settings = {
    'bar_spacing': 15,
    'bar_width': 8,
    'max_values' : 8,
    'label_index': 2    
}

week_settings = {
    'bar_spacing': 15,
    'bar_width': 8,
    'max_values' : 8,
    'label_index': 2    
}

month_settings = {
    'bar_spacing': 15,
    'bar_width': 8,
    'max_values' : 8,
    'label_index': 1   
}

quarter_settings = {
    'bar_spacing': 15,
    'bar_width': 10,
    'max_values' : 6,
    'label_index': 1
}

# Generic
bar_x_offset = 2

energy_y_min = 10
energy_y_max = 32

gas_y_min = 56
gas_y_max = 32

mode = 'day' # Current mode
display_consumption(mode)

# Loop and wait
start = time.time()

while True:
    if time.time() - start > (60 * 60): # Refresh every hour
        start = time.time() # Reset
        display_consumption(mode)
        
    # Change mode
    if gp.switch_pressed(SWITCH_A):
        change_mode('day')
    elif gp.switch_pressed(SWITCH_B):
        change_mode('week')
    elif gp.switch_pressed(SWITCH_C):
        change_mode('month')        
    elif gp.switch_pressed(SWITCH_D):
        change_mode('quarter')
    elif gp.switch_pressed(SWITCH_E):
        display_about()
        
    time.sleep(0.1) # Lower values make button more responsive


