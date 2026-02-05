import smbus   
import time


bus = smbus.SMBus(1)
channels = [0x40, 0x41, 0x42, 0x43]


def setup(Addr):
    global address
    address = Addr


def read(chn):
    global address
    bus.write_byte(address, channels[chn])
    bus.read_byte(address)
    return bus.read_byte(address)


def write(val):
    bus.write_byte_data(address, 0x40, int(val))


if __name__ == '__main__':
    setup(0x48)
    while True:
        print('Light intensity: ', read(0))
        print('temperature: ', read(1) - 234)
        time.sleep(1)

