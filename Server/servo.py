import time
from board import SCL, SDA
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685


i2c = busio.I2C(SCL, SDA)
# Create a simple PCA9685 class instance.
pca = PCA9685(i2c, address=0x40) #default 0x40

pca.frequency = 50

def set_angle(ID, angle):
    servo_angle = servo.Servo(pca.channels[ID], min_pulse=500, max_pulse=2400,actuation_range=180)
    servo_angle.angle = angle

def test(channel):
    for i in range(180):
        set_angle(channel, i)
        time.sleep(0.01)
    time.sleep(0.5)
    for i in range(180):
        set_angle(channel, 180-i)
        time.sleep(0.01)
    time.sleep(0.5)

if __name__ == "__main__":
    channel = 0
    while True:
        test(channel)

'''

'''

#servo7.angle = 90
