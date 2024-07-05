import can
import time

max_speed = 5

init_speed_mode = [[0x2B, 0x0F, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00],
[0x2F, 0x60, 0x60, 0x00, 0x03, 0x00, 0x00, 0x00],
[0x23, 0x83, 0x60, 0x01, 0x64, 0x00, 0x00, 0x00],
[0x23, 0x83, 0x60, 0x02, 0x64, 0x00, 0x00, 0x00],
[0x23, 0x84, 0x60, 0x01, 0x64, 0x00, 0x00, 0x00],
[0x23, 0x84, 0x60, 0x02, 0x64, 0x00, 0x00, 0x00],
[0x2B, 0x40, 0x60, 0x00, 0x06, 0x00, 0x00, 0x00],
[0x2B, 0x40, 0x60, 0x00, 0x07, 0x00, 0x00, 0x00],
[0x2B, 0x40, 0x60, 0x00, 0x0F, 0x00, 0x00, 0x00],]

def init(bus):
    
    for i in range(9):
        msg = can.Message(arbitration_id=0x601, data=init_speed_mode[i], is_extended_id=False)
        bus.send(msg)
    
    return True

def int_to_bytes_list(number:int):
    if number < 0:
        number = 0xFFFFFFFF + number + 1
    return  [ number & 0xFF, (number >> 8) & 0xFF, (number >> 16) & 0xFF, (number >> 24) & 0xFF,]

def set_speed(bus, left_speed:int, right_speed:int):
    
    left_speed = int(left_speed)
    right_speed = int(right_speed)

    left_msg = can.Message(arbitration_id=0x601, data=[0x23, 0xff, 0x60, 0x01]+int_to_bytes_list(left_speed), is_extended_id=False)
    right_msg = can.Message(arbitration_id=0x601, data=[0x23, 0xff, 0x60, 0x02]+int_to_bytes_list(right_speed), is_extended_id=False)

    bus.send(left_msg)
    time.sleep(0.01)
    bus.send(right_msg)
    time.sleep(0.01)


def stop_wheel(bus):
    msg = can.Message(arbitration_id=0x601, data=[0x2b, 0x40, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00], is_extended_id=False)
    bus.send(msg)

def turn_left(bus, left_speed=-max_speed, right_speed=max_speed):
    set_speed(bus, left_speed, -right_speed)
    time.sleep(5)  # TBD
    stop_wheel(bus)
    
def turn_right(bus, left_speed=max_speed, right_speed=-max_speed):
    set_speed(bus, left_speed, -right_speed)
    time.sleep(1) # TBD
    stop_wheel(bus)
    
if __name__ == "__main__":
    bus = can.interface.Bus(interface='slcan', channel='/dev/ttyACM0', bitrate=500000)
    init(bus)
    
    while True:
        c = input()
        print("get:", c)
        left_speed = 0
        right_speed = 0
        
        if c == 'w' or c == 'W':
            left_speed = max_speed
            right_speed = -max_speed
        elif c == 'a' or c == 'A':
            left_speed = -max_speed
            right_speed = -max_speed
        elif c == 's' or c == 'S':
            left_speed = -max_speed
            right_speed = max_speed
        elif c == 'd' or c == 'D':
            left_speed = max_speed
            right_speed = max_speed
        elif c == 'q' or c == 'Q':
            stop_wheel(bus)
            continue
        elif c == ',' or c == '<':
            turn_left(bus)
            continue
        elif c == '.' or c == '>':
            turn_right(bus)
            continue

        set_speed(bus, left_speed, right_speed)
        time.sleep(0.5)
        
    bus.shutdown()