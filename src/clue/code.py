from adafruit_clue import clue
from adafruit_display_text import label
#import adafruit_imageload
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

import rotaryio
import board
import digitalio
import displayio
import terminalio
import adafruit_imageload

encoder = rotaryio.IncrementalEncoder(board.D0, board.D1)
autofocus = digitalio.DigitalInOut(board.D2)
autofocus.direction = digitalio.Direction.INPUT
autofocus.pull = digitalio.Pull.UP

FRIENDS_NAME = "random"
autofocus_state = None
last_position = None

display = clue.display
disp_group = displayio.Group()
display.show(disp_group)

# Background BMP with the Morse Code cheat sheet
bmp, pal = adafruit_imageload.load("morse_bg.bmp",
                                   bitmap=displayio.Bitmap,
                                   palette=displayio.Palette)
disp_group.append(displayio.TileGrid(bmp, pixel_shader=pal))

# Incoming messages show up here
in_label = label.Label(terminalio.FONT, text='A'*18, scale=2,
                       color=0x000000)
in_label.anchor_point = (0.5, 0)
in_label.anchored_position = (65, 12)
disp_group.append(in_label)

# Outging messages show up here
out_label = label.Label(terminalio.FONT, text='B'*18, scale=2,
                        color=0x000000)
out_label.anchor_point = (0.5, 0)
out_label.anchored_position = (65, 190)
disp_group.append(out_label)

# Morse Code entry happens here
edit_label = label.Label(terminalio.FONT, text='....', scale=2,
                         color=0x000000)
edit_label.anchor_point = (0.5, 0)
edit_label.anchored_position = (105, 222)
disp_group.append(edit_label)

def scan_and_connect():
    '''
    Advertise self while scanning for friend. If friend is found, can
    connect by pressing A+B buttons. If friend connects first, then
    just stop.

    Return is a UART object that can be used for read/write.
    '''

    print("Advertising.")
    central = False
    ble.start_advertising(advertisement)

    print("Waiting.")
    friend = None
    while not ble.connected:

        if friend is None:
            print("Scanning.")
            in_label.text = out_label.text = "Scanning..."
            for adv in ble.start_scan():
                print(adv.complete_name)
                if ble.connected:
                    # Friend connected with us, we're done
                    ble.stop_scan()
                    break
                if adv.complete_name == FRIENDS_NAME:
                    # Found friend, can stop scanning
                    ble.stop_scan()
                    friend = adv
                    print("Found", friend.complete_name)
                    in_label.text = "Found {}".format(friend.complete_name)
                    out_label.text = "A+B to connect"
                    break
        else:
            if clue.button_a and clue.button_b:
                # Connect to friend
                print("Connecting to", friend.complete_name)
                ble.connect(friend)
                central = True

    # We're now connected, one way or the other
    print("Stopping advertising.")
    ble.stop_advertising()

    # Return a UART object to use
    if central:
        print("Central - using my UART service.")
        return uart_service
    else:
        print("Peripheral - connecting to their UART service.")
        for connection in ble.connections:
            if UARTService not in connection:
                continue
            return connection[UARTService]

ble = BLERadio()
uart_service = UARTService()
advertisement = ProvideServicesAdvertisement(uart_service)
ble._adapter.name = "focus-control" #pylint: disable=protected-access

#uart = scan_and_connect()

while True:
    position = encoder.position
    if last_position is None or position != last_position:
        in_label.text = out_label.text = position
        print(position)
    last_position = position
    if not autofocus.value and autofocus_state is None:
        autofocus_state = "pressed"
    if autofocus.value and autofocus_state == "pressed":
        print("Button pressed.")
        autofocus_state = None