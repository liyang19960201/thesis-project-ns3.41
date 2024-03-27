from ns import ns #The NS package from python

from matplotlib import pyplot as plt
import sys
from csv import DictReader
import pandas as pd
import re


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
filename="node-test.csv" 

# nodeposition=pd.read_csv(filename)

# print(nodeposition)

def loadposition(wifiStaNodes :ns.NodeContainer):
    nodeposition = {}
    coordinate=[]

    global coordinatesHistoric


    with open(filename, 'r') as file:
        reader = DictReader(file)
        print(reader)
       

        mobilityHelper = ns.MobilityHelper()
        mobilityHelper.SetMobilityModel ("ns3::WaypointMobilityModel")
        # mobilityHelper.SetPositionAllocator ("ns3::randomBoxPositions")
        mobilityHelper.Install (wifiStaNodes)


        for entry in reader:

            print((int(entry["Node ID"]))-1)
            node = wifiStaNodes.Get((int(entry["Node ID"]))-1)
            print(node)
            mobility = node.GetObject[ns.WaypointMobilityModel]().__deref__()
            
            # time = ns.Seconds(abs(float(entry["Timestamp"])))
            
            print(abs(float(entry["Timestamp"])))
            nextPos = ns.Vector(float(entry["x"]), float(entry["y"]), float(entry["z"]))
            print(nextPos)
            # wpt = ns.Waypoint (time, nextPos)
            # print(wpt)

            # mobility.AddWaypoint(wpt)
            currPos = nextPos

            print(node,currPos)
        
        # ids=reader['Track'].tolist()
        # vc=reader['Vehicle'].tolist()
        # ds=reader['Description'].tolist()
        # ts=reader['Translation'].apply(eval).tolist()
        # tsmp=ns.core.Simulator.Now()

        # print(ids)
        # print(vc)
        # print(ds)
        # print(ts[0][0])
        # print(ts[0][1])
        # print(tsmp)
    # print(len(reader))

      
    # for index in range(len(reader)):
        
    #         track=ids[index]
    #         vehicle=ds[index]
    #         x,y=ts[index][0],ts[index][1]
    #         timestamp=ns.core.Simulator.Now()
    #         nodeposition = (x, y)
    #         linePositions = ns.CreateObject("ListPositionAllocator")
    #         linePositions.__deref__().Add (ns.Vector(x, y, 0))
            
           
           
           
    #         mobilityHelper = ns.MobilityHelper()
            

    #         mobilityHelper.SetPositionAllocator (linePositions)
    #         mobilityHelper.Install(wifiStaNodes)
    #         mobility = wifiStaNodes.Get(1).GetObject[ns.MobilityModel]().__deref__()
    #         position = mobility.GetPosition()
    #         coordinate = ((position.x), (position.y))
    #         coordinatesHistoric.append((vehicle, nodeposition))
    #         print(coordinate,end="\n") 

    # print(ns.Simulator.Now().GetSeconds(),end="\n")
    # event = ns.pythonMakeEvent(loadposition,wifiStaNodes)
    # ns.Simulator.Schedule(ns.Seconds(0.5),event)
    # print(coordinatesHistoric)
          
        
def animateSimulation():
    global coordinatesHistoric
    
    # Save a copy and clean historic for the next animation
    coordinatesHistoricCopy = coordinatesHistoric.copy()
    coordinatesHistoric = []
    
    # Animate coordinates from the simulation
    from matplotlib import pyplot as plt
    from matplotlib.animation import FuncAnimation
    animations=[]
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
        plt.legend(handles, labels,loc='upper left')
       
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
    animations.append(anim)
   
    plt.show()
    plt.close()
    return

            



mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
#Configue a constant position model for access point nodes
mobility.Install(wifiApNodes)
#Connect constatnt model to ap wifi nodes


loadposition(wifiStaNodes)

# animateSimulation()
# getNodeCoordinates(wifiStaNodes)


ns.core.Simulator.Stop(ns.core.Seconds(10.0))
#Simulation steops at 10.0s


   

ns.core.Simulator.Run()


#Advancing simulation clock and executing schduled events
ns.core.Simulator.Destroy()

#Clean up and destoy the simulatin environment, and releasing allocated resources.



