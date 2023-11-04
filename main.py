try:
    import utime as time
except ImportError:
    import time

from microdot import Microdot, send_file, Response
import os
import camera
from ubinascii import hexlify
from machine import Pin

import neopixel

# Setup the neopixel
np = neopixel.NeoPixel(Pin(12), 16)
import ujson

app = Microdot()

flash = Pin(4, Pin.OUT)
camera_initialized = False
streaming = False

Response.default_content_type = 'text/html'

def random_filename():
    random_bytes = os.urandom(4)
    return "bc_" + hexlify(random_bytes).decode() + ".jpg"

def capture_frame(flash_enabled):
    if flash_enabled:
        flash.value(1)
        time.sleep(0.5)
    frame = camera.capture()
    if flash_enabled:
        flash.value(0)
    return frame

def setup_camera(settings=None):
    global camera_initialized
    if camera_initialized:
        return
    camera.init()
    camera_initialized = True
    if settings:
        for setting, value in settings.items():
            if hasattr(camera, setting):
                setattr(camera, setting, value)
    else:
        # Default camera settings
        camera.framesize(11)
        camera.contrast(2)
        camera.speffect(0)
        camera.agcgain(0)
        camera.aecvalue(0)
        camera.aelevels(0)
        camera.brightness(0)
        camera.quality(10)
        camera.whitebalance(0)
        camera.saturation(0)

def image_dump():
    if not camera_initialized:
        return
    for _ in range(10):
        camera.capture()
        
@app.route('/birdhouse-cam-low-resolution-color-logo.jpeg')
def logo_low(request):
    return send_file('birdhouse-cam-low-resolution-color-logo.jpeg', compressed=True,
                     file_extension='.gz')

@app.route('/birdhouse-cam-high-resolution-color-logo.jpeg')
def logo_hi(request):
    return send_file('birdhouse-cam-high-resolution-color-logo-new.jpeg', compressed=True,
                     file_extension='.gz')

@app.route('/birdhouse-cam-website-favicon-black.png')
def favi(request):
    return send_file('birdhouse-cam-website-favicon-black.png', compressed=True,
                     file_extension='.gz')

@app.route('/gear.png')
def gear(request):
    return send_file('gear.png')

@app.route('/birdhouse-cam-bowlby-one-sc-regular.ttf')
def font(request):
    return send_file('birdhouse-cam-bowlby-one-sc-regular.ttf')

@app.route('/')
def index(request):
    return send_file('ws_root.html')

@app.route('/live')
def live(request):
    return send_file('ws_live.html')

@app.route('/settings')
def settings(request):
    return send_file('ws_settings.html')

@app.route('/settings.json')
def json(request):
    return send_file('settings.json')

@app.route('/filename')
def list_name(request):
    global filename  # access the global filename variable
    filename = random_filename()
    return filename

@app.route('/stopstream')
def stop_stream(request):
    global streaming  # access the global streaming variable
    streaming = False
    return send_file('ws_root.html')

@app.route('/pic')
def pic(request):
    return send_file('ws_pic.html')

@app.route('/fpic')
def fpic(request):
    return send_file('ws_pic.html')

@app.route('/foto')
def foto(request):
    global last_captured_frame, filename
    
    try:
        referer = request.headers.get('Referer', '')
        flash_enabled = '/fpic' in referer
        last_captured_frame = capture_frame(flash_enabled)
        
        # Ensure that the response is constructed correctly
        headers = {'Content-Type': 'image/jpeg'}
        return Response(last_captured_frame, headers=headers, status_code=200)
    except Exception as e:
        print(f"Error capturing frame: {e}")
        return Response('Internal Server Error', status_code=500)

@app.route('/stream')
def video_feed(request):
    global streaming
    streaming = True
    def stream():
        yield b'--frame\r\n'
        while streaming:
            frame = capture_frame(False)
            yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'
    return stream(), 200, {'Content-Type': 'multipart/x-mixed-replace; boundary=frame'}

@app.route('/savesettings', methods=['POST'])
async def save_settings(request):
    settings = await request.json
    with open('settings.json', 'w') as settings_file:
        settings_file.write(ujson.dumps(settings))
    setup_camera(settings)
    return Response(ujson.dumps({"message": "Settings saved successfully!"}), content_type='application/json')

@app.route('/control_lights', methods=['POST'])
async def control_lights(request):
    data = await request.json()
    if data is None:
        return Response(ujson.dumps({'error': 'No data provided'}), status_code=400, content_type='application/json')
    color = data.get('color')
    brightness = int(data.get('brightness'))

    # Define colors
    colors = {
        'red': (brightness, 0, 0),
        'green': (0, brightness, 0),
        'blue': (0, 0, brightness),
        'orange': (brightness, 165, 0),
        'purple': (128, 0, 128),
        'yellow': (brightness, brightness, 0),
        'white': (brightness, brightness, brightness),
        'warm': (255, 224, 189)  # Warm light
    }

    # Set the color
    if color in colors:
        np[0] = colors[color]
        np.write()

    return Response(ujson.dumps({"message": "Lights updated successfully!"}), content_type='application/json')


if __name__ == '__main__':
    setup_camera()
    image_dump()
    app.run(host='', port=80)