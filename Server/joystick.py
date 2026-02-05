import gpiozero
import PCF8591 as ADC
import time

btn = gpiozero.Button(
    17, 
    pull_up=True  
)

STATE_LIST = ['home', 'down', 'up', 'left', 'right', 'pressed']

def setup():
    # Initialize PCF8591 ADC (address 0X48)
    ADC.setup(0X48)

def direction():
    i = 0  
    
    adc_ch0 = ADC.read(0)
    if adc_ch0 <= 5:
        i = 1  # down
    elif adc_ch0 >= 200:
        i = 2  # up
    
    adc_ch1 = ADC.read(1)
    if adc_ch1 <= 5:
        i = 3  # left
    elif adc_ch1 >= 200:
        i = 4  # right
    
    if btn.is_pressed:
        i = 5  # pressed
    
    adc_ch2 = ADC.read(2)
    if not btn.is_pressed and (-15 < adc_ch1 - 125 < 15) and adc_ch2 == 255:
        i = 0
    
    return STATE_LIST[i]

def loop():
    current_status = ''
    while True:
        new_status = direction()
        if new_status and new_status != current_status:
            print(new_status)
            current_status = new_status
        time.sleep(0.1)  # reduce loop frequency

def destroy():
    btn.close()

if __name__ == '__main__':
    try:
        setup()
        loop()
    except KeyboardInterrupt:  # Capture Ctrl+C to exit
        destroy()
        print("\nProgram exited, resources cleaned up")