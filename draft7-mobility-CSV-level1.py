from ns import ns #The NS package from python

from matplotlib import pyplot as plt
import sys
import csv
import pandas as pd
import re

#The system module in python, in this case, it will sever
#for the cmd section

from ctypes import c_bool, c_int
#The certain types from ctypes moduel in python, which
#is providing c++ compatible data types, in this case.
#int and bool datatypes

nCsma = c_int(3)
#The number of nodes in CSMA subnet, c_int is the integer
#from ctype
verbose = c_bool(True)
#The variable to enable/disable log component, c_boolean is the integer
#from ctype
nWifi = c_int(3)
#The number of nodes in wifi subnet, c_int is the integer
#from ctype
tracing = c_bool(True)
#The variable to enable/disable tracing, c_int is the integer
#from ctype


cmd = ns.CommandLine(__file__)
#A command line parser(cmd) using comandLine class from ns-3
#__file__ is a variable represents name of current scripts in python
#CommandLine is an object with scripts'name
cmd.AddValue("nCsma", "Number of extra CSMA nodes/devices", nCsma)
#A commandline argument to the parser,it allows script to accept
#parameter 'nCsma' with a description following, the value
#of this paramter is provided during execution as '3'
cmd.AddValue("nWifi", "Number of wifi STA devices", nWifi)
#A commandline argument to the parser,it allows script to accept
#parameter 'nwifi' with a description following, the value
#of this paramter is provided during execution as '3'
cmd.AddValue("verbose", "Tell echo applications to log if true", verbose)
#A commandline argument to the parser,it allows script to accept
#parameter 'verbose' with a description following, the value
#of this paramter is provided during execution as 'true'
cmd.AddValue("tracing", "Enable pcap tracing", tracing)
#A commandline argument to the parser,it allows script to accept
#parameter 'tracing' with a description following, the value
#of this paramter is provided during execution as 'false'
cmd.Parse(sys.argv)
#Command-line parser is assignning with 'sys.argv', it
#has command-line argument passed to the scripts.
#It also has values from parameters with their related variables.



if nWifi.value > 18:
    print("nWifi should be 18 or less; otherwise grid layout exceeds the bounding box")
    sys.exit(1)
# The underlying restriction of 18 is due to the grid position
# allocator's configuration; the grid layout will exceed the
# bounding box if more than 18 nodes are provided.

if verbose.value:
    ns.core.LogComponentEnable("BulkSendApplication", ns.core.LOG_LEVEL_FUNCTION)
    ns.core.LogComponentEnable("PacketSink", ns.core.LOG_LEVEL_FUNCTION)
    

#If value for verbose is true, then enabling logcomponent,
#the components are capturing and displaying execution infomration.
#Method 1 to generate output but with performance compromise.
    



wifiStaNodes = ns.network.NodeContainer() 
#Create an empty container for wifi nodes

wifiStaNodes.Create(4)
#Create the number of 'nwifi.value' nodes from wifi container
wifiApNodes = ns.network.NodeContainer() 
wifiApNodes.Create(1)

#Get the first node from p2p node container
#Define this node as the access point, not functionally




mobility = ns.mobility.MobilityHelper()
#Creare a mobility helper object to conifgure node mobility

mobility.SetPositionAllocator(
    "ns3::GridPositionAllocator",
    "MinX",
    ns.core.DoubleValue(0.0),
    "MinY",
    ns.core.DoubleValue(0.0),
    "DeltaX",
    ns.core.DoubleValue(5.0),
    "DeltaY",
    ns.core.DoubleValue(10.0),
    "GridWidth",
    ns.core.UintegerValue(3),
    "LayoutType",
    ns.core.StringValue("RowFirst"),
)
#Configure a grid-based position allocator for nodes,the
#parameters are minimum of X and Y coordinates, grid spacing
#and layout type, it can be tunned later accordingly



   

######Mobility section1
def logNodePositionStep1(nodeContainer : ns.NodeContainer, showLegend: bool = True) -> None:
    for node_i in range(nodeContainer.GetN()):
        node = nodeContainer.Get(node_i).__deref__()
        mobility = node.GetObject[ns.MobilityModel]().__deref__()
        position = mobility.GetPosition()
        print("Node {}, Position: ({}, {}, {})".format(node.GetId(), position.x, position.y, position.z))
    
       
        
######Mobility section2--dynamic
coordinatesHistoric = []

# Create an event in C++ for the following python function
ns.cppyy.cppdef("""
   #ifndef pymakeevent
   #define pymakeevent
   namespace ns3
   {
       EventImpl* pythonMakeEvent(void (*f)(NodeContainer&), NodeContainer& nodes)
       {
           return MakeEvent(f, nodes);
       }
   }
   #endif
""")

def getNodeCoordinates(nodeContainer : ns.NodeContainer) -> None:
    global coordinatesHistoric

    coordinates = {}
    for node_i in range(nodeContainer.GetN()):
        node = nodeContainer.Get(node_i).__deref__()
        mobility = node.GetObject[ns.MobilityModel]().__deref__()
        position = mobility.GetPosition()
        coordinates[f"Node {node.GetId()}"] = ((position.x), (position.y))
        
    coordinatesHistoric.append((ns.Simulator.Now().GetSeconds(), coordinates))
    print(ns.Simulator.Now().GetSeconds(),end="\n")
    print(coordinates,end="\n")
  
  

    # Re-schedule after every 1 second
    event = ns.pythonMakeEvent(getNodeCoordinates, nodeContainer)
    ns.Simulator.Schedule(ns.Seconds(1), event)
    




#####

#######csv section
# Read CSV file with node positions
filename="node_positions.csv" 

nodeposition=pd.read_csv(filename)

print(nodeposition)

def loadposition(filename):
    nodeposition = {}

    global coordinatesHistoric


    with open(filename, 'r') as file:
        reader = pd.read_csv(file)
        
        ids=reader['Node ID'].tolist()
        cx=reader['Position X'].tolist()
        cy=reader['Position Y'].tolist()
        tsmp=reader['Timestamp'].tolist()

        # print(ids)
        # print(cx)
        # print(cy)
        # print(tsmp)


      
    for i in range(3):
        for j in range(4):
            index = i * 4 + j
            if index >= len(ids):
                break
            node_id=ids[index]
            x,y=cx[index],cy[index]
            timestamp=ns.core.Simulator.Now().GetSeconds()
            nodeposition = (x, y)
            linePositions = ns.CreateObject("ListPositionAllocator")
            linePositions.__deref__().Add (ns.Vector(x, y, 0))
           
           
            mobilityHelper = ns.MobilityHelper()
            mobilityHelper.SetMobilityModel ("ns3::ConstantPositionMobilityModel")

            mobilityHelper.SetPositionAllocator (linePositions)
            mobilityHelper.Install(wifiStaNodes.Get(j))
            mobility = wifiStaNodes.Get(j).GetObject[ns.MobilityModel]().__deref__()
            position = mobility.GetPosition()
           
            print(f"{node_id} is locating in {position} at {timestamp}")
            coordinatesHistoric.append((node_id,nodeposition))
    print(coordinatesHistoric)
          
        
def animateSimulation():
    global coordinatesHistoric
    
    # Save a copy and clean historic for the next animation
    coordinatesHistoricCopy = coordinatesHistoric.copy()
    coordinatesHistoric = []
    
    # Animate coordinates from the simulation
    from matplotlib import pyplot as plt
    from matplotlib.animation import FuncAnimation
    
    fig = plt.figure()
    lines = {}

    
    def init():
        # Initialize animation artists
        for (node, position) in coordinatesHistoricCopy:
            
            lines[node], = plt.plot([position[0]], [position[1]], label=node)
       
        
        # Create a legend containing all nodes without repeated entries
        handles, labels = [], []
        unique_labels = set()
        for (node, position) in coordinatesHistoricCopy:
            if node not in unique_labels:
                handles.append(lines[node])
                labels.append(node)
                unique_labels.add(node)
        plt.legend(handles, labels)
        # Determine animation boundss
        x_bounds = [999999, 0]
        y_bounds = [999999, 0]
        for (_, position) in coordinatesHistoricCopy:
            if position[0] < x_bounds[0]:
                x_bounds[0] = position[0]
            if position[0] > x_bounds[1]:
                x_bounds[1] = position[0]
            if position[1] < y_bounds[0]:
                y_bounds[0] = position[1]
            if position[1] > y_bounds[1]:
                y_bounds[1] = position[1]
        
        # Add a margin to the bounds
        x_bounds[0] -= 1
        y_bounds[0] -= 1
        x_bounds[1] += 1
        y_bounds[1] += 1
        
        # Set animation bounds
        plt.xlim(x_bounds)
        plt.ylim(y_bounds)
    
    def animate(i):
        for node, position in coordinatesHistoricCopy:
            x_data = list(lines[node].get_xdata()) + [position[0]]
            y_data = list(lines[node].get_ydata()) + [position[1]]
            lines[node].set_data(x_data, y_data)
    
    # Animate the historic of coordinates
    anim = FuncAnimation(fig, animate, init_func=init,
                         frames=len(coordinatesHistoricCopy),
                         interval=5, repeat=True)
   
    plt.show()
    plt.close()
    return

            


#Connect mobility model on station wifi nodes

mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
#Configue a constant position model for access point nodes
mobility.Install(wifiApNodes)
#Connect constatnt model to ap wifi nodes


loadposition(filename)

animateSimulation()
# getNodeCoordinates(wifiStaNodes)


ns.core.Simulator.Stop(ns.core.Seconds(10.0))
#Simulation steops at 10.0s


   

ns.core.Simulator.Run()



#Advancing simulation clock and executing schduled events
ns.core.Simulator.Destroy()

#Clean up and destoy the simulatin environment, and releasing allocated resources.



