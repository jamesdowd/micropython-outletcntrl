#outlet 0.5.0
import time
import machine
from umqtt.simple import MQTTClient
import ujson
import sys
import esp
from ntptime import settime
import utime
#import scheduler

esp.osdebug(None)

print("Outlet Transmitter: MQTT Code")

def transmit(switch_cntrl, light1,light2,sw, topic,name="outlet_default", server="192.168.1.90",err_slp=100,err_rst=150):
	print("Starting MQTT transmitter...")

	#save the start time
	(syear, smonth, smday, shour, sminute, ssecond, sweekday, syearday) = utime.localtime()

	#configure switch pins
	outlet_switch = machine.Pin(sw, machine.Pin.OUT)
	outlet_light1 = machine.Pin(light1, machine.Pin.OUT)
	outlet_light2 = machine.Pin(light2, machine.Pin.OUT)
	outlet_cntrl = machine.Pin(switch_cntrl, machine.Pin.IN, machine.Pin.PULL_UP)

	#set the outlet to the default state
	outlet_switch.off()
	outlet_light1.off()

	#flash the blue light so user has indication that outlet is working
	outlet_light2.on()
	time.sleep(.25)
	outlet_light1.on()
	time.sleep(.25)
	outlet_light1.off()
	time.sleep(.25)
	outlet_light1.on()
	time.sleep(.25)
	outlet_light1.off()
	time.sleep(.25)
	outlet_light1.on()

	#define the channels
	btopic=bytes(topic,'utf-8')
	state_channel=btopic
	command_channel=btopic+b'/set'
	availability_channel=btopic+b'/available'
	debug_channel='debug'

	#set up udp socket
	c = MQTTClient(name, server)
	c.set_last_will(topic=availability_channel, msg=b'offline', retain=False, qos=0)
	c.connect()
	print("Started!")
	
	#notify that you're available
	c.publish(availability_channel, b'online')

	def dbg_msg(name, msg):
		#debug messages
		payload = {}
		payload["outlet_name"]=name
		payload["message"]=msg
		a=ujson.dumps(payload)
		c.publish(debug_channel, a)

	dbg_msg(name,'switch boot up')

	#status
	def status():
		(year, month, mday, hour, minute, second, weekday, yearday) = utime.localtime()
		
		print("")
		print("")
		print("Outlet v.0.5.0")
		print ("{}/{}/{} {}:{}:{} | boot: {}/{}/{} {}:{}:{}".format(month,mday,year,hour,minute,second,smonth,smday,syear,shour,sminute,ssecond))
		print ("Error Count: {}".format(str(error_cnt)))
		print("")
		print("Outlet status: "+str(outlet_switch.value()))
		print("Outlet name: " + name)
		print("Outlet topic: " + topic)

		dbg_msg(name,"Outlet status: "+str(outlet_switch.value()))

	#mqtt callback
	def monitor_cmds(topic,msg):
		if msg == b"ON":
			outlet_switch.on()
			try:
				c.publish(state_channel, b'ON')
				dbg_msg(name,'switch commanded on')

			except:
				print("Error - Publish On!")
				rst_comm()
				error_cnt+=1
			outlet_light1.off()
			outlet_light2.on()

		elif msg == b"OFF":
			outlet_switch.off()
			try:
				c.publish(state_channel, b'OFF')
				dbg_msg(name,'switch commanded off')
			except:
				print("Error - Publish Off!")
				rst_comm()
				error_cnt+=1
			outlet_light1.on()
			outlet_light2.on()

		#elif msg == b"schedule update":
		#elif msg == b"request schedule":
		#elif msg == b"schedule message":
		#elif msg == b"control selection":
		#elif msg == b"reboot":

	#phyisical button
	def btn_cntrl(p):
		time.sleep(1)
		if outlet_cntrl.value() == 0:
			if outlet_switch.value() == 0:
				monitor_cmds('',b'ON')
			else:
				monitor_cmds('',b'OFF')

		#debug messages
		dbg_msg(name,'physical button pressed')

	def rst_comm():
		c.disconnect()
		c.connect()
		c.subscribe(command_channel)
		dbg_msg(name,'device reset')
			
	#set interrupts
	c.set_callback(monitor_cmds)
	outlet_cntrl.irq(handler=btn_cntrl,trigger=outlet_cntrl.IRQ_FALLING)

	#subscribe to the command channel
	c.subscribe(command_channel)

	#wait
	error_cnt=0
	while True:
		try:
			#check the command channel
			c.check_msg()
		except:
			print("Error - Check Message!")

			#reboot the connection
			rst_comm()
			error_cnt+=1

		#print status to the repl
		try:
			status()
		except:
			print("Error - Status")
			error_cnt+=1

		#watch error count, reset if limit exceeded
		if error_cnt ==err_slp:
			time.sleep(15)
		elif error_cnt >err_rst:
			machine.reset()

		#Wait for a second
		time.sleep(1)

	c.disconnect()
	print('exiting...')
