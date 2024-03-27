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


mobilityHelper = ns.MobilityHelper()

mobilityHelper.SetMobilityModel ("ns3::WaypointMobilityModel")
mobilityHelper.SetPositionAllocator(
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
# mobilityHelper.SetPositionAllocator (randomBoxPositions)
mobilityHelper.Install (wifiStaNodes)

#######csv section
# Read CSV file with node positions
filename="testmobilty.csv" 


with open(filename,"r") as f:
    movements = DictReader(f)
    print(movements)

    for entry in movements:
        print(entry)
        node = wifiStaNodes.Get(int(entry["node"]))
        mobility = node.GetObject[ns.WaypointMobilityModel]().__deref__()
        time = ns.Seconds(int(entry["time"]))
        nextPos = ns.Vector(int(entry["x"]), int(entry["y"]), 0)
        wpt = ns.Waypoint (time, nextPos)
        mobility.AddWaypoint(wpt)
        currPos = nextPos


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

getNodeCoordinates(wifiStaNodes)

ns.core.Simulator.Stop(ns.core.Seconds(10.0))
#Simulation steops at 10.0s
ns.core.Simulator.Run()
#Advancing simulation clock and executing schduled events
ns.core.Simulator.Destroy()    



#Get the first node from p2p node container
#Define this node as the access point, not functionally



####Setting the address
address = ns.internet.Ipv4AddressHelper()

address.SetBase(ns.network.Ipv4Address("10.1.3.0"), ns.network.Ipv4Mask("255.255.255.0"))
#Ser the base IPv4 address and subnet mask(for wifi)
stainterface=address.Assign(staDevices)
#connect address to station wifi interfaces(decvies)
apinterface=address.Assign(apDevices)

