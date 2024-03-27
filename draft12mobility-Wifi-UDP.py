from ns import ns #The NS package from python

from matplotlib import pyplot as plt
import sys
from csv import DictReader
import pandas as pd
import re

tracing =1
wifiStaNodes = ns.network.NodeContainer() 
#Create an empty container for wifi nodes

wifiStaNodes.Create(4)
#Create the number of 'nwifi.value' nodes from wifi container
wifiApNodes = ns.network.NodeContainer() 
wifiApNodes.Create(1)

####Wifi Underlying Channel

channel = ns.wifi.YansWifiChannelHelper.Default()
#Create a channel by using defrault Yet Another Network Simulator
#channel model, this channel servers for communication between wireless nodes

phy = ns.wifi.YansWifiPhyHelper()
#Create a helper object to configure physical layer of Wifi nodes
#Still use Yans
phy.SetChannel(channel.Create())
#Related to phy from previousline, create the channel with
#physical layer. Outter line is setting chaneel for wifi nodes
#By default, the WifiHelper (the typical use case for WifiPhy creation) will
#configure the WIFI_STANDARD_80211ax standard by default. 

#####Standard definiation undefined
# ns.wifi.SetStandard(WIFI_STANDAR4.Two clients with one server (UDP)----How two client communicate through the server???​D_80211n)
phy.Set("ChannelSettings", ns.core.StringValue("{0, 40, BAND_5GHZ, 0}"))
#the operating channel will be channel 38 in the 5 GHz band,
#which has a width of 40 MHz, and the primary20 channel will be the 20 MHz
#subchannel with the lowest center frequency (index 0).

mac = ns.wifi.WifiMacHelper()
#Create a helper object to configure MAC layer of wifi nodes
ssid = ns.wifi.Ssid("ns-3-ssid")
#Create a ssid for wifi network, which identifies a wifi network

wifi = ns.wifi.WifiHelper()
#Create a helper object to set up wifi network

mac.SetType(
    "ns3::StaWifiMac", "Ssid", ns.wifi.SsidValue(ssid), "ActiveProbing", ns.core.BooleanValue(False)
)
#Set the type of MAC layer for station devices as 'ns3::StaWifiMac'
#Applied SSID for station device from precious definition
#Disable active probling from station device with ns.core.Boolean
staDevices = wifi.Install(phy, mac, wifiStaNodes)
#Connect station device with station wifi nodes, applying precious
#physical and MAC layer settings, store them in staDevices
mac.SetType("ns3::ApWifiMac", "Ssid", ns.wifi.SsidValue(ssid))
#Set the type of MAC layers for access point devices as 'ns3::ApWifiMac'
#for AP devices
#Applied SSID for AP devices as same as STA devices

apDevices = wifi.Install(phy, mac, wifiApNodes)
#Connect AP devices to AP wifi nodes, applying same physcial
#and MAC layer seetings, store them in apDevices


stack = ns.internet.InternetStackHelper()
#Create an internetstack helper object to configure and install
#internet protocol stacks on nodes

# stack.Install(csmaNodes)
stack.Install(wifiApNodes)
stack.Install(wifiStaNodes)




###Mobility Module
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


mobilityHelper.SetMobilityModel("ns3::ConstantPositionMobilityModel")
#Configue a constant position model for access point nodes
mobilityHelper.Install(wifiApNodes)
#Connect constatnt model to ap wifi nodes

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


    
def animateSimulation():
    global coordinatesHistoric
    
    # Save a copy and clean historic for the next animation
    coordinatesHistoricCopy = coordinatesHistoric
    coordinatesHistoric = []
    


    # Animate coordinates from the simulation
    from matplotlib import pyplot as plt
    from matplotlib.animation import FuncAnimation
 
    
    fig = plt.figure()
    lines = {}
    def init():
        # Initialize animation artists
        for (node, coordinate) in coordinatesHistoricCopy[0][1].items():
            lines[node], = plt.plot([coordinate[0]], [coordinate[1]], label=node)

        # Determine animation bounds
        x_bounds = [999999,0]
        y_bounds = [999999,0]
        for i in range(len(coordinatesHistoricCopy)):
            for (node, coordinate) in coordinatesHistoricCopy[i][1].items():
                if (coordinate[0] < x_bounds[0]):
                    x_bounds[0] = coordinate[0]
                if (coordinate[0] > x_bounds[1]):
                    x_bounds[1] = coordinate[0]
                if (coordinate[1] < y_bounds[0]):
                    y_bounds[0] = coordinate[1]
                if (coordinate[1] > y_bounds[1]):
                    y_bounds[1] = coordinate[1]
                
         
   
                    
        # Add a margin to the bounds
        x_bounds[0] -= 1
        y_bounds[0] -= 1
        x_bounds[1] += 1
        y_bounds[1] += 1
        
        # Set animation bounds
        plt.xlim(x_bounds)
        plt.ylim(y_bounds)
       


        

    def animate(i):
        for (node, coordinate) in coordinatesHistoricCopy[i][1].items():
            x_data = list(lines[node].get_xdata()) + [coordinate[0]]
            y_data = list(lines[node].get_ydata()) + [coordinate[1]]
            lines[node].set_data(x_data, y_data)
            
    
    # Animate the historic of coordinates
    anim = FuncAnimation(fig, animate, init_func=init,
                         frames = len(coordinatesHistoricCopy),
                         interval = 100, repeat=True)
            

  
    plt.show()
    plt.close()
    return






ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

#Addressing
address = ns.internet.Ipv4AddressHelper()

address.SetBase(ns.network.Ipv4Address("10.1.3.0"), ns.network.Ipv4Mask("255.255.255.0"))
#Ser the base IPv4 address and subnet mask(for wifi)
stainterface=address.Assign(staDevices)
#connect address to station wifi interfaces(decvies)
apinterface=address.Assign(apDevices)


##Servers
echoServer = ns.applications.UdpEchoServerHelper(9)
#Create UDP echo server helper object to listen on port 9
serverApps = echoServer.Install(wifiStaNodes.Get(3))
#Connect a UDP echo server application to CSMA node with index
# vlaue=predefined 3
serverApps.Start(ns.core.Seconds(1.0))
#Time to start server application at 1.0s
serverApps.Stop(ns.core.Seconds(10.0))
#Time to stop server application at 10.0s

#Client
serveraddr=stainterface.GetAddress(3).ConvertTo()
print(stainterface.GetAddress(0))
echoClient = ns.applications.UdpEchoClientHelper(serveraddr,9)
#Create a UDP echo client helper object, sending packets to
#IPv4 address from CSMA interfaces at index 'ncsma.value' and on port 9



echoClient.SetAttribute("MaxPackets", ns.core.UintegerValue(10))
#Configure the maximum number of packets that UDP echo client
#will send to the servers, it is 1 here
echoClient.SetAttribute("Interval", ns.core.TimeValue(ns.core.Seconds(1.0)))
#Configure time interval between two packets, it is 1.0s
echoClient.SetAttribute("PacketSize", ns.core.UintegerValue(1024))
#Configure every packet size as 1024 bytes
clientApps = echoClient.Install(wifiStaNodes.Get(0))
#Connect UDP echo client application to wifi node with index
#nwifi.value-1 since it started from 0
clientApps.Start(ns.core.Seconds(2.0))
#Time to start client application at 2.0s
clientApps.Stop(ns.core.Seconds(10.0))
#Time to stop client application at 10.0s





if tracing==0:
#This section only execute if tracing is enabled
    phy.SetPcapDataLinkType(phy.DLT_IEEE802_11_RADIO)
    #Set packet capture data link type for wifi physical layer
    #to IEEE 802.11 in standard format
    # pointToPoint.EnablePcapAll("draft")
    #It enable tracing for p2p devices, 'thirdis output file name

    phy.EnablePcap("draft", apDevices.Get(0))
getNodeCoordinates(wifiStaNodes)

ns.core.Simulator.Stop(ns.core.Seconds(10.0))
#Simulation steops at 10.0s
ns.core.Simulator.Run()

animateSimulation()
#Advancing simulation clock and executing schduled events
ns.core.Simulator.Destroy()    