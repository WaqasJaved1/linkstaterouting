from socket import*
import time
from threading import Thread
import datetime

#some constants
re_check_off_time = 1;
off_time = 4;
re_check_send_time = 2;

#Variable to store config file data
data = []

status =[]

#Server
serverSocket = socket(AF_INET, SOCK_DGRAM)

def startServer(port):
	serverSocket.bind(('', port))


def readconfig(name):
	#
	global data;
	data = [data.rstrip('\n') for data in open(name)]

	index = 0;
	for x in data:
		data[index] = x.split(" ")	
		data[index].insert(3, False)
		data[index].insert(4, datetime.datetime.now())
		index = index+1

def checkRouterState():
	for x in range(1, int(data[0][0])+1):
		packet = "0:" + data[x][2];
		packet = packet.encode("utf-8")
		serverSocket.sendto(packet, ("localhost", int(data[x][2])))
		print("Checking: ", int(data[x][2]))

def HandlecheckRouterState():
	global serverSocket, data
	while True:
		try:
			message, addr = serverSocket.recvfrom(1024) # buffer size is 1024 bytes
			message = message.decode('utf-8').split(':')
			#print("received message: ", message)


			if(message[0] == '0'):
				packet = "1:"+message[1];
				packet = packet.encode("utf-8");
				serverSocket.sendto(packet, addr)
			elif(message[0] == '1'):
				print("Port Alive: " + message[1])
				for x in range(1, int(data[0][0])+1):
					if (data[x][2] == message[1]):
						data[x][3] = True;
						data[x][4] = datetime.datetime.now();
						break;

		except Exception as e:
			pass
			#print(e)

def checkOffRouters():
	while True:
		for x in range(1,int(data[0][0])+1):
			if((datetime.datetime.now() - data[x][4]).seconds > off_time):
				data[x][3] = False;
				data[x][4] = datetime.datetime.now()

		time.sleep(re_check_off_time)

startServer(5001)
readconfig('configA.txt');
r = Thread(target=HandlecheckRouterState)
r.daemon = True
r.start()

t = Thread(target=checkOffRouters)
t.daemon = True
t.start();

while True:
	time.sleep(re_check_send_time);
	checkRouterState()
	print(data);

#print(datetime.datetime.now());