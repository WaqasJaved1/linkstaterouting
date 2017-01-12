#solve circular dependency

from socket import*
import time
from threading import Thread
import datetime
import sys
from copy import deepcopy
import dijkstra_d


#some constants
re_check_off_time = 1;
off_time = 3;
re_check_send_time = 1;
broadcast_delay = 1;
off_time_broadcast = 3;

#Variable to store config file data
data = [];

router_name = sys.argv[1]
seq_number = 0;
seq_number_i = 0;
no_of_neighbours = 0;

graph = {};
graph_time_update = {};
#variable to store broadcast message
broad_cast_msg = "";

check_last_time = {}

#Server
serverSocket = socket(AF_INET, SOCK_DGRAM)

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

	# graphPrint();


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
						# print(e)
						pass
					


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
				print(y[0]+"("+y[1]+")," , end="")
	
			print("\n")		

		print ("--------------------------------------------");

	except:
		pass
	

def autoPrint():
	x = 0;
	while True:
		print ("+++++++++++++++:: ", str(x));
		graphPrint();
		# print(graph)
		time.sleep(2);

# def call_dikstra():		
# 	while True:
# 		try:
# 			localgraph = deepcopy(graph);
# 			di_graph = dijkstra.Graph();

# 			#inserting Nodes
# 			for x in localgraph:
# 				print(router_name, x, type(router_name), type(x))
# 				di_graph.add_node(str(router_name), str(x));

# 			#inserting Edges
# 			for x in localgraph:
# 				for y in graph[x]["data"]:
# 					di_graph.add_edge(router_name, x, y[0], y[1] )


# 			visited,path = dijsktra.dijsktra(di_graph, router_name);
# 			print (visited, path)
# 		except Exception as e:
# 			print(e)

# 		time.sleep(2);

def call_dikstra():
	while True:

		try:
			localgraph = deepcopy(graph)
			G = {}
			for x in graph:
				G[x] = {}
				for y in localgraph[x]["data"]:
					G[x][y[0]] = float(y[1])

			# print(G)

			print("_______________")
			print("I am router ", router_name)

			for x in graph:
				if x != router_name:
					path = dijkstra_d.shortestPath(G, router_name, x)
					print("Least cost path to router ",x,":",  end="")

					# print(path)
					cost = 0;

					for x in range(0, len(path)-1):
						cost += G[path[x]][path[x+1]]
						print(path[x], end="")

					print(path[len(path)-1],end="")

					print(" and the cost: ",end = "")
					print("%.1f" % cost)

			print("_______________")

		except Exception as e:
			print(e)
			pass
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

d = Thread(target=call_dikstra)
d.daemon = True;
d.start();


while True:
	time.sleep(re_check_send_time);
	checkRouterState()

	#print(seq_number);

#print(datetime.datetime.now());