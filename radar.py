import serial,sys,glob
import serial.tools.list_ports as COMs
from pylab import *

# Ports (Windows only)
ports = ['COM{0:1.0f}'.format(ii) for ii in range(1,256)]

arduino_ports = []
for port in ports: # loop through to determine if accessible
    if len(port.split('Bluetooth'))>1: continue
    try:
        serial.Serial(port).close()
        arduino_ports.append(port) # if we can open it, consider it an arduino
    except (OSError, serial.SerialException):
        pass

if not arduino_ports: print("Aucune Arduino branchée !")
else: print("Ports susceptibles:", arduino_ports)

ser = serial.Serial(arduino_ports[0],baudrate=115200) # match baud on Arduino
ser.flush() # clear the port

# Matplotlib
started = False
points = []
print("En attente du demarrage de l'Arduino...")


fig, ax = plt.subplots()
fig.canvas.mpl_connect('close_event', sys.exit)

plt.title('Visualisation radar')
plt.ion()

while True:
    """ser_bytes = ser.readline() # read Arduino serial data
    decoded_bytes = ser_bytes.decode('utf-8') # decode data to utf-8
    data = (decoded_bytes.replace('\r','')).replace('\n','')

    if data=='Radar Start': print("Start !"); started = True
    if not started: continue"""

    vals = [0, 0, randint(0,359), (randint(15,250))]#[float(x) for x in data.split(',')]
    # [0, 0, randint(0,359), (randint(15,250))] - points ayant servi pour le test. plt.pause(.2)
    x, y, angle_robot, distance = vals

    rotation = array([
        [cos(angle_robot), -sin(angle_robot)],
        [sin(angle_robot), cos(angle_robot)]
    ])

    # le robot est toujours orienté vers le haut de l'écran
    points.append(np.array((x,y)) + distance * rotation * np.array((0,-1)))
    
    # Dessiner nuage de points
    points_x = [p[0] for p in points]
    points_y = [p[1] for p in points]
    plt.scatter(points_x, points_y, c='blue', label='Points', marker='.')
    plt.scatter(x, y, c='red', label='Rond', marker='o')

    plt.draw()