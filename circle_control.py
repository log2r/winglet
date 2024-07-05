import can
import time

L = 0.25  # 左右轮间距

def calculate_wheel_speeds(radius, speed, direction):
    omega = speed / radius
    left_speed = speed - direction * omega * (L / 2)
    right_speed = speed + direction * omega * (L / 2)
    return left_speed, right_speed

init_speed_mode = [
    [0x2B, 0x0F, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00],
    [0x2F, 0x60, 0x60, 0x00, 0x03, 0x00, 0x00, 0x00],
    [0x23, 0x83, 0x60, 0x01, 0x64, 0x00, 0x00, 0x00],
    [0x23, 0x83, 0x60, 0x02, 0x64, 0x00, 0x00, 0x00],
    [0x23, 0x84, 0x60, 0x01, 0x64, 0x00, 0x00, 0x00],
    [0x23, 0x84, 0x60, 0x02, 0x64, 0x00, 0x00, 0x00],
    [0x2B, 0x40, 0x60, 0x00, 0x06, 0x00, 0x00, 0x00],
    [0x2B, 0x40, 0x60, 0x00, 0x07, 0x00, 0x00, 0x00],
    [0x2B, 0x40, 0x60, 0x00, 0x0F, 0x00, 0x00, 0x00],
]

def init(bus):
    for i in range(9):
        msg = can.Message(arbitration_id=0x601, data=init_speed_mode[i], is_extended_id=False)
        bus.send(msg)
        # print("Sent: \t", msg)
        # try:
        #     recv = bus.recv(timeout=1)
        #     if recv:
        #         print("Received: \t", recv)
        #     else:
        #         print("No response")
        # except can.CanError as e:
        #     print("Error receiving:", e)
        time.sleep(0.1)
    return True

def int_to_bytes_list(number: int):
    if number < 0:
        number = 0xFFFFFFFF + number + 1
    return [number & 0xFF, (number >> 8) & 0xFF, (number >> 16) & 0xFF, (number >> 24) & 0xFF]

def set_speed(bus, left_speed: int, right_speed: int):
    left_speed = int(left_speed)
    right_speed = int(right_speed)

    left_msg = can.Message(arbitration_id=0x601, data=[0x23, 0xFF, 0x60, 0x01] + int_to_bytes_list(left_speed), is_extended_id=False)
    right_msg = can.Message(arbitration_id=0x601, data=[0x23, 0xFF, 0x60, 0x02] + int_to_bytes_list(right_speed), is_extended_id=False)

    bus.send(left_msg)
    time.sleep(0.01)
    bus.send(right_msg)
    time.sleep(0.01)


def stop_wheel(bus):
    msg = can.Message(arbitration_id=0x601, data=[0x2b, 0x40, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00], is_extended_id=False)
    bus.send(msg)

if __name__ == "__main__":
    bus = can.interface.Bus(interface='slcan', channel='/dev/ttyACM0', bitrate=500000)
    init(bus)
    
    radius = float(input("Enter the radius of the circle: "))
    speed = float(input("Enter the speed of the robot: "))
    direction = int(input("Enter the direction: "))

    left_speed, right_speed = calculate_wheel_speeds(radius, speed, direction)

    try:
        while True:
            set_speed(bus, left_speed, -right_speed)
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_wheel(bus)
        
    bus.shutdown()
    