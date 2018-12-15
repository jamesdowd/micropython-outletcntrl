#outlet 0.5.0
import outlet_v5
from time import sleep
#TYWE3S: 4 blue, 5 nc, sw/red led 12, btn 13
#TYWE2S: 4 blue, 5 red, sw 12, btn 13

#sleep(2)
#sensor main
sensor_name = "livingroom"
server = "192.168.1.90"
status_light1 = 4
status_light2 = 5
outlet_switch = 12
switch_cntrl = 13
topic = 'home/outlets/'+sensor_name
#topic = 'home/bedroom/switch4'

print("Outlet Transmitter: "+sensor_name)

outlet_v5.transmit(switch_cntrl, status_light1,status_light2,outlet_switch,topic,sensor_name, server)
