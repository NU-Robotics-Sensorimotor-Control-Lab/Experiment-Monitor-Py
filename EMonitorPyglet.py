"""EMonitorPyglet

Replaces .NET EMonitor for experiment at Northwestern RSC Lab

Press escape to exit!!!

Worklog:
J. Bremen, July 2021
 - Created program

 - NOTE!! This file does not change based on state; always displays the circle
"""

import socket, struct, ifaddr, pyglet


class EMonitor:
    def __init__(self, ip="localhost", port=5005, screen_index=0):
        self.n_sounds = 13

        # Initialize the target forces
        self.target_tor = 1
        self.up_lim_tor = 1
        self.target_tor = 1
        self.match_tor = 1
        self.low_lim_tor = 1

        # Initialize Force Parameters
        self.targetF = 1
        self.up_limF = 1
        self.low_limF = 1
        self.matchF = 1

        self.sound_trigger = [False for i in range(self.n_sounds)]
        self.sounds_playing = list([False] * self.n_sounds)
        self.players = []

        self.stop_trigger = 0

        # UDP Stuff
        self.UDP_IP = ip
        self.UDP_PORT = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.UDP_IP, self.UDP_PORT))

        # Makes the socket nonblocking
        self.sock.setblocking(0)

        # Graphics stuff below here
        self.thread_running = True

    def unpack_bytes_to_double(self, bytes):
        return struct.unpack("d", bytes)[0]

    def unpack_udp_package(self, data):
        """
        Validate package size in bytes first

        Bytes structured as:
        0-7: Target Torque (double)
        8-15: Target Low Limit Torque (double)
        16-23: Target Up Limit Torque (double)
        24-31: Currently produced torque (double)

        32-39: Target Force NM (double)
        40-47: Target Low Limit Force (double)
        48-55: Target Upper Limit Force (double)
        56-63: Currently produced force (double)

        64:64+n_sounds-1- one boolean byte for each sound cue (bool)
        64+n_sounds- one byte representing if sounds should be stopped (bool)
        """
        if len(data) != 65 + self.n_sounds:
            print("ERROR!")
            return

        self.target_tor = self.unpack_bytes_to_double(data[0:8])
        self.low_lim_tor = self.unpack_bytes_to_double(data[8:16])
        self.up_lim_tor = self.unpack_bytes_to_double(data[16:24])
        self.match_tor = self.unpack_bytes_to_double(data[24:32])

        self.targetF = self.unpack_bytes_to_double(data[32:40])
        self.low_limF = self.unpack_bytes_to_double(data[40:48])
        self.up_limF = self.unpack_bytes_to_double(data[48:56])
        self.matchF = self.unpack_bytes_to_double(data[56:64])

        for i in range(self.n_sounds):
            self.sound_trigger[i] = bool(data[64 + i])

        self.stop_trigger = data[64 + self.n_sounds]

    def recieve_single_udp(self, dt):
        # Function clears udp buffer and uses the most recent udp message
        # dt will not be used, but we need to give an extra input for pyglet
        data = None

        while True:
            try:
                # This 1460 buffer size is connected to the buffer size in the
                # MATLAB sending code; can likely be reduced for slightly
                # faster IO
                data, addr = self.sock.recvfrom(1460)

            except BlockingIOError:
                break

        if data:
            self.unpack_udp_package(data)


# Ethernet setup
# First, get the IP address
ip = None

for adapter in ifaddr.get_adapters():
    if adapter.ips[0].nice_name == "Ethernet":
        ip = [x.ip for x in adapter.ips]

ETHERNET_IP = None
PORT = 5005

if ip:
    for i in ip:
        if type(i) == str and i.count(".") == 3:
            ETHERNET_IP = i

if not ETHERNET_IP:
    print("Issue detecting ethernet interface!")
    print("Reverting to localhost ip")
    ETHERNET_IP = "localhost"

print("Using Ethernet IP:", ETHERNET_IP)
print("Using Ethernet Remote Port", PORT)

"""
    NOTE
    
    ETHERNET NOTES!

    If issues with ethernet connection arise, I recommend first unplugging
    and replugging in the ethernet wires in the switch (all of them)

    If this fails, restart the PC with the Ethernet cable unplugged

    If the NU Ethernet system is down, do not plug the Ethernet wire into the 
    switch; this will prevent the computer from creating its own local ip

    If the connection starts being slow, check the ping speeds with cmd prompt

    Odds are it's due to a loose wire
"""

# Define RGB colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 175)
RED = (255, 0, 0)

SCREEN_INDEX = 1

display = pyglet.canvas.get_display()
screens = display.get_screens()
event_loop = pyglet.app.EventLoop()

if len(screens) <= SCREEN_INDEX:
    print("Using default display")
    SCREEN_INDEX = 0

print(f"{SCREEN_INDEX = }")

# Create objects for the pyglet window and fps display
window = pyglet.window.Window(fullscreen=True, screen=screens[SCREEN_INDEX])
fps_display = pyglet.window.FPSDisplay(window=window)

# set background color as white
pyglet.gl.glClearColor(*WHITE, 255)

# Load the sounds
SOUND_DIRECTORY = "soundCues\\"
FILE_NAMES = [
    "hold.wav",
    "in.wav",
    "out.wav",
    "match.wav",
    "relax.wav",
    "startingtrial.wav",
    "endingtrial.wav",
    "Out of Range.wav",
    "Wrong Direction.wav",
    "in.wav",
    "out.wav",
    "up.wav",
    "down.wav",
]

SOUND_CUES = []
for file in FILE_NAMES:
    n = SOUND_DIRECTORY + file

    # print(f"Loading {n}")

    SOUND_CUES.append(pyglet.media.load(n, streaming=False))
print(f"Loaded {len(SOUND_CUES)} / {len(FILE_NAMES)} sounds successfully")

# Initialize the EMonitor
emonitor = EMonitor(ETHERNET_IP, PORT)


@event_loop.event
def on_window_close(window):
    print("Hey")
    event_loop.exit()
    return pyglet.event.EVENT_HANDLED


def custom_draw_circle_one_thick(x_center, y_center, radius, color, batch):
    # Implements mid-point circle drawing algorithm

    X = radius
    Y = 0

    points = []

    points.append([X + x_center, y_center])
    points.append([x_center + X, y_center])
    points.append([x_center - X, y_center])

    points.append([x_center, y_center + X])
    points.append([x_center, y_center - X])

    if radius > 0:
        points.append([X + x_center, -Y + y_center])
        points.append([Y + x_center, X + y_center])
        points.append([-Y + x_center, X + y_center])

    P = 1 - radius

    while X > Y:
        Y += 1

        # Midpoint is inside or on the perimeter
        if P <= 0:
            P = P + 2 * Y + 1

        else:
            X -= 1
            P = P + 2 * Y - 2 * X + 1

        if X < Y:
            break

        points.append([X + x_center, Y + y_center])
        points.append([-X + x_center, Y + y_center])
        points.append([X + x_center, -Y + y_center])
        points.append([-X + x_center, -Y + y_center])

        if X != Y:
            points.append([Y + x_center, X + y_center])
            points.append([-Y + x_center, X + y_center])
            points.append([Y + x_center, -X + y_center])
            points.append([-Y + x_center, -X + y_center])

    num_points = len(points)
    # Concatanate points list; gl expects list in format [x0, y0, x1, y1...]
    collapsed_points = [j for i in points for j in i]

    color_list = color * num_points

    batch.add(
        num_points,
        pyglet.gl.GL_POINTS,
        None,
        ("v2i", collapsed_points),
        ("c3B", color_list),
    )


def custom_draw_circle(x_center, y_center, radius, color, thickness, batch):
    edges = min(thickness, radius)

    for t in range(edges):
        rad = radius - t

        custom_draw_circle_one_thick(x_center, y_center, rad, color, batch)


def draw_circle(x, y, radius, color, bg_color, thickness, batch):
    a = pyglet.shapes.Circle(x, y, radius, color=color, batch=batch)
    b = None

    if radius - (2 * thickness) > 0:
        b = pyglet.shapes.Circle(
            x, y, radius - (2 * thickness), color=bg_color, batch=batch
        )

    return [a, b]


def draw_full_line(y, length, color, width, batch):
    return pyglet.shapes.Line(0, y, length, y, width=width, color=color, batch=batch)


@window.event
def on_draw():
    pyglet.clock.tick()

    try:
        WIDTH = window.width
        HEIGHT = window.height

        center_x = WIDTH // 2
        center_y = HEIGHT // 2

        # Define the radii of the circles
        m = emonitor

        match_target_radius = int(HEIGHT / 1.5)
        targetF_line = center_y

        if m.target_tor == 0:
            m.target_tor = 1

        if m.targetF == 0:
            m.targetF = 1

        lower_range_radius = int(match_target_radius * (m.low_lim_tor / m.target_tor))
        upper_range_radius = int(match_target_radius * (m.up_lim_tor / m.target_tor))
        representation_radius = int(match_target_radius * (m.match_tor / m.target_tor))

        # Code to set the moving Y coordinates

        lowF_line = targetF_line * (m.low_limF / m.targetF)
        upF_line = targetF_line * (m.up_limF / m.targetF)

        # The C# Code has matchY = center_y * ((2 - m.matchF) / m.targetF)
        # i'm not sure why the 2.0 - is present though, so I deleted it
        # This might have to be reintroduced sometime, or could be a side
        # effect of the way that # does graphics
        matchY = center_y * ((m.matchF) / m.targetF)

        # Need to sort the radii, as the circles will draw on top of each other
        radii = sorted(
            [
                (match_target_radius, BLACK),
                (lower_range_radius, BLUE),
                (upper_range_radius, BLUE),
            ],
            key=lambda t: t[0],
            reverse=True,
        )

        lines = [
            (lowF_line, BLUE),
            (upF_line, BLUE),
            (matchY, RED),
            (targetF_line, BLACK),
        ]

        batch = pyglet.graphics.Batch()

        # Using a array to hold the graphics objects, to ensure that they
        # aren't destroyed before being drawn
        a = []

        for radius in radii:
            a.append(draw_circle(center_x, center_y, *radius, WHITE, 3, batch))

        for line in lines:
            a.append(draw_full_line(line[0], WIDTH, line[1], 3, batch))

        # The custom drawing function is very slow, so only use it for the
        # moving circle. Perhaps make this better someday?

        window.clear()
        fps_display.draw()
        batch.draw()

        # Make a new batch to ensure that openGL optimization does not
        # erase the moving circle
        batch = pyglet.graphics.Batch()
        custom_draw_circle(center_x, center_y, representation_radius, RED, 3, batch)
        batch.draw()

        # Sound stuff here
        for i in range(emonitor.n_sounds):
            if emonitor.sound_trigger[i] and not emonitor.sounds_playing[i]:
                # print(f"Sound {i} is playing")
                emonitor.players.append(SOUND_CUES[i].play())
                emonitor.sounds_playing[i] = True

        if emonitor.stop_trigger:
            # print("Stop sounds")
            while emonitor.players:
                emonitor.players.pop().pause()
            emonitor.sounds_playing = [False] * emonitor.n_sounds

    except ZeroDivisionError:
        print("Zero division detected")
        fps_display.draw()
        pass


if __name__ == "__main__":
    # Call the update function to be run on every frame
    pyglet.clock.schedule(emonitor.recieve_single_udp)

    pyglet.app.run()
