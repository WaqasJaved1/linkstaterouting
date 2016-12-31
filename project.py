#solve circular dependency

from socket import*
import time
from threading import Thread
import datetime
import sys
from copy import deepcopy

#some constants
re_check_off_time = 1;
off_time = 4;
re_check_send_time = 2;
broadcast_delay = 1;
off_time_broadcast = 5;

#Variable to store config file data
data = [];

router_name = sys.argv[1]
seq_number = 0;
seq_number_i = 0;
no_of_neighbours = 0;

graph = {};
graph_time_update = {};
#variable to store broadcast message
broad_cast_msg = "2?Null";

check_last_time = {}

#Server
serverSocket = socket(AF_INET, SOCK_DGRAM)

def dijsktra(graph, initial):
  visited = {initial: 0}
  path = {}

  nodes = set(graph.nodes)

  while nodes: 
    min_node = None
    for node in nodes:
      if node in visited:
        if min_node is None:
          min_node = node
        elif visited[node] < visited[min_node]:
          min_node = node

    if min_node is None:
      break

    nodes.remove(min_node)
    current_weight = visited[min_node]

    for edge in graph.edges[min_node]:
      weight = current_weight + graph.distance[(min_node, edge)]
      if edge not in visited or weight < visited[edge]:
        visited[edge] = weight
        path[edge] = min_node

  return visited, path

def startServer():
	serverSocket.bind(('', int(sys.argv[2])))


def connection_state_changed():
	global seq_number, broad_cast_msg;
	temp = {};
	temp['data'] = [value for value in data if value[3] == True];
	temp['seq'] = seq_number;
	temp['time'] = datetime.datetime.now();

	broad_cast_msg = "2?"+ router_name + "?"+str(temp);

	seq_number = seq_number +1;

	graph[router_name] = temp;

	graphPrint();


def handleBroadcast(message, sender, orignal_message):
	global check_last_time;


	if(message[1] != router_name):
		obj = eval(message[2]);

		check = False

		temp = 0;
		temp2= 0;
		if(message[1] in graph):
			temp = int(deepcopy(message[3]))
			temp2 = int(deepcopy(check_last_time[message[1]]['seq']))
		
			
		#print(message[4],message[1],temp, temp2, temp > temp2)

		if(message[1] not in graph):
			check_last_time[message[1]] = {}
			check_last_time[message[1]]['time'] = datetime.datetime.now();
			check_last_time[message[1]]['seq'] = message[3];
		elif(temp> temp2):

			check_last_time[message[1]]['time'] = datetime.datetime.now();
			check_last_time[message[1]]['seq'] = message[3];
			check = True;

		if(message[1] not in graph):
			graph[message[1]] = obj;
			#graphPrint();

		elif(graph[message[1]]["seq"] != obj["seq"]):
			graph[message[1]] = obj;
			#graphPrint();

					
		if check:
			for x in range(0,no_of_neighbours):
				if(int(data[x][2]) != sender):
					try:
						#print("sending to: "+ data[x][0])
						serverSocket.sendto(orignal_message, ("localhost", int(data[x][2])))
					except Exception as e:
						print(e)
					


def readconfig():
	#
	global data, no_of_neighbours;
	data = [data.rstrip('\n') for data in open(sys.argv[3])]

	index = 0;
	for x in data:
		data[index] = x.split(" ")	
		data[index].insert(3, False)
		data[index].insert(4, datetime.datetime.now())
		index = index+1

	no_of_neighbours = int(data[0][0]);
	data.pop(0)
	connection_state_changed()

def checkRouterState():
	for x in range(0, no_of_neighbours):
		packet = "0?" + data[x][2];
		packet = packet.encode("utf-8")
		serverSocket.sendto(packet, ("localhost", int(data[x][2])))
		#print("Checking: ", int(data[x][2]))

def HandlecheckRouterState():
	global serverSocket, data
	while True:
		try:
			message, addr = serverSocket.recvfrom(1024) # buffer size is 1024 bytes
			orignal_message = message;
			message = message.decode('utf-8').split('?')
			#print("received message: ", message)


			if(message[0] == '0'):
				packet = "1?"+message[1];
				packet = packet.encode("utf-8");
				serverSocket.sendto(packet, addr)
			elif(message[0] == '1'):
				#print("Port Alive: " + message[1])
				for x in range(0, no_of_neighbours):
					if (data[x][2] == message[1]):
						data[x][4] = datetime.datetime.now();
						if(data[x][3] == False):
							data[x][3] = True;
							connection_state_changed();
						break;
			elif(message[0] == '2'):
				th = Thread(target=handleBroadcast, args=(message, addr[1], orignal_message))
				th.daemon = True
				th.start();
				# if(message[1] != router_name):
				# 	obj = eval(message[2]);
				# 	# graphPrint();
				# 	# print("__________________________")
				# 	# print(message[1]+ "::::::::::"+ str(obj))
				# 	# print("__________________________")

				# 	check = False



				# 	print(message[1],message[3]);
				# 	if(message[1] not in graph):
				# 		check_last_time[message[1]] = {}
				# 		check_last_time[message[1]]['time'] = datetime.datetime.now();
				# 		check_last_time[message[1]]['seq'] = message[3];
				# 	elif(int(check_last_time[message[1]]['seq']) < int(message[3]) ):
				# 		check_last_time[message[1]]['time'] = datetime.datetime.now();
				# 		check_last_time[message[1]]['seq'] = message[3];
				# 		True;

				# 	if(message[1] not in graph):
				# 		graph[message[1]] = obj;
				# 		#graphPrint();

				# 	elif(graph[message[1]]["seq"] != obj["seq"]):
				# 		graph[message[1]] = obj;
				# 		#graphPrint();

					
				# 	if check:
				# 		for x in range(0,no_of_neighbours):
				# 			if(int(data[x][2]) != addr[1]):
				# 				serverSocket.sendto(orignal_message, ("localhost", int(data[x][2])))

		except Exception as e:
			pass
			#print(e)

def checkOffRouters():
	while True:
		for x in range(0,no_of_neighbours):
			if((datetime.datetime.now() - data[x][4]).seconds > off_time and data[x][3] == True):
				data[x][3] = False;
				data[x][4] = datetime.datetime.now()
				connection_state_changed();
		

		time.sleep(re_check_off_time)

def checkExpiredRouters():
	while True:
		try:

			for x in check_last_time:
				if((datetime.datetime.now() - check_last_time[x]["time"]).seconds > off_time_broadcast):
					graph.pop(x, None);
					check_last_time.pop(x,None);
		except:
			pass

		time.sleep(re_check_off_time)

def generateBroadcaste():
	global seq_number_i
	while True:
		for x in range(0,no_of_neighbours):
			serverSocket.sendto((broad_cast_msg+"?"+str(seq_number_i)+"?"+router_name).encode("utf-8"), ("localhost", int(data[x][2])))
		
		seq_number_i= seq_number_i+1;
		time.sleep(broadcast_delay);

	
def graphPrint():
	try:
		print ("--------------------------------------------");
		
		for x in graph:
			print (x+":->", end="");
	
			for y in graph[x]["data"]:
				print(y[0]+"," , end="")
	
			print("\n")		

		print ("--------------------------------------------");

	except:
		pass
	

def autoPrint():
	x = 0;
	while True:
		print ("+++++++++++++++:: ", str(x));
		graphPrint();
		time.sleep(2);

def call_dikstra():
	while True:
		result = dijsktra(graph, 'A');
		print(result)
		time.sleep(2);

startServer()
readconfig();
r = Thread(target=HandlecheckRouterState)
r.daemon = True
r.start()

t = Thread(target=checkOffRouters)
t.daemon = True
t.start();

b = Thread(target=generateBroadcaste)
b.daemon = True
b.start();

e = Thread(target=checkExpiredRouters)
e.daemon = True
e.start();

a = Thread(target=autoPrint)
a.daemon = True;
a.start();

while True:
	time.sleep(re_check_send_time);
	checkRouterState()

	#print(seq_number);

#print(datetime.datetime.now());