import Adafruit_BluefruitLE
import os
from Adafruit_BluefruitLE.services import UART


uart = None

def sendCommand(msg ):
    try:
        if msg == "on":
            command = 'curl -H "Content-type: application/json" \'http://192.168.1.23/cm?user=argex&password=argex1q2w3e4r&cmnd=Power%20ON\''
            os.system (command)
        if msg == "off":
            command = 'curl -H "Content-type: application/json" \'http://192.168.1.23/cm?user=argex&password=argex1q2w3e4r&cmnd=Power%20OFF\''
            os.system (command)

    except KeyboardInterrupt:
        print ("exit!")

# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()


# Main function implements the program logic so it can run in a background
# thread.  Most platforms require the main thread to handle GUI events and other
# asyncronous events like BLE actions.  All of the threading logic is taken care
# of automatically though and you just need to provide a main function that uses
# the BLE provider.

def initBle():
    # Clear any cached data because both bluez and CoreBluetooth have issues with
    # caching data and it going stale.
    ble.clear_cached_data()
    
    # Get the first available BLE network adapter and make sure it's powered on.
    adapter = ble.get_default_adapter()
    adapter.power_on()
    print('Using adapter: {0}'.format(adapter.name))
    
    # Disconnect any currently connected UART devices.  Good for cleaning up and
    # starting from a fresh state.
    print('Disconnecting any connected UART devices...')
    UART.disconnect_devices()

     # Scan for UART devices.
    print('Searching for UART device...')
    try:
        adapter.start_scan()
        # Search for the first UART device found (will time out after 60 seconds
        # but you can specify an optional timeout_sec parameter to change it).
        device = UART.find_device()
        if device is None:
            raise RuntimeError('Failed to find UART device!')
    finally:
        # Make sure scanning is stopped before exiting.
        adapter.stop_scan()

    print('Connecting to device...')
    device.connect()  # Will time out after 60 seconds, specify timeout_sec parameter
                      # to change the timeout.
    return device


def main():
    device = initBle()

    # Once connected do everything else in a try/finally to make sure the device
    # is disconnected when done.
    try:
        # Wait for service discovery to complete for the UART service.  Will
        # time out after 60 seconds (specify timeout_sec parameter to override).
        print('Discovering services...')
        UART.discover(device)

        # Once service discovery is complete create an instance of the service
        # and start interacting with it.
        global uart
        uart = UART(device)
        print(uart)
        # Write a string to the TX characteristic.
        uart.write(b'Hello world!\r\n')
        #print("Sent 'Hello world!' to the device.")

        # Now wait up to one minute to receive data from the device.
        while True:
        #print('Waiting up to 60 seconds to receive data from the device...')
            received = uart.read(timeout_sec=60)
            if received is not None:
                # Received data, print it out.
                print('Received: {0}'.format(received))
            else:
                # Timeout waiting for data, None is returned.
                print('Received no data!')
                continue
            sendCommand(received)
            #sendCommandDrone("state?")
    finally:
        # Make sure device is disconnected on exit.
        device.disconnect()


# Initialize the BLE system.  MUST be called before other BLE calls!
ble.initialize()

# Start the mainloop to process BLE events, and run the provided function in
# a background thread.  When the provided main function stops running, returns
# an integer status code, or throws an error the program will exit.
ble.run_mainloop_with(main)



