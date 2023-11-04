import network
import time

def setup_sta(ssid, password):
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    
    # Check if already connected
    if sta.isconnected():
        print("Already connected")
        return
    
    print("Connecting to network...")
    sta.connect(ssid, password)
    
    while not sta.isconnected():
        print('Waiting for connection...')
        time.sleep(1)
    
    print("Network connection established")
    print("Network configuration:", sta.ifconfig())
    
# Function to set up a Wi-Fi access point
def setup_ap(SSID, PASSWORD):
    ap = network.WLAN(network.AP_IF)
    ap.active(True)

    print("Setting up Wi-Fi access point...")
    ap.config(essid=SSID, password=PASSWORD, authmode=network.AUTH_WPA_WPA2_PSK)
    ap.ifconfig(('12.25.20.22', '255.255.255.0', '12.25.20.1', '8.8.8.8'))

    print("Access Point active!")
    print("Network configuration:", ap.ifconfig())

# Wi-Fi credentials
SSID = "Birdhouse-Cam"
PASSWORD = "tagme100"

ssid = "C-IOT 2.4"
password = "BrownOrange18#"

# Set up Wi-Fi Station
setup_sta(ssid, password)
# Set up Wi-Fi access point
#setup_ap(SSID, PASSWORD)
