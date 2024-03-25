from ns import ns #The NS package from python


import sys

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
    ns.core.LogComponentEnable("UdpEchoClientApplication", ns.core.LOG_LEVEL_DEBUG)
    ns.core.LogComponentEnable("UdpEchoServerApplication", ns.core.LOG_LEVEL_DEBUG)
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


mobility.SetMobilityModel(
    "ns3::RandomWalk2dMobilityModel",
    "Bounds",
    ns.mobility.RectangleValue(ns.mobility.Rectangle(-50, 50, -50, 50)),
)

#Configure a 2D random wlak mobel model for nodes, the boundary
#of this model is a rectangle with 100 wide and long
mobility.Install(wifiStaNodes)
#Connect mobility model on station wifi nodes

mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
#Configue a constant position model for access point nodes
mobility.Install(wifiApNodes)
#Connect constatnt model to ap wifi nodes

stack = ns.internet.InternetStackHelper()
#Create an internetstack helper object to configure and install
#internet protocol stacks on nodes

# stack.Install(csmaNodes)
stack.Install(wifiApNodes)
stack.Install(wifiStaNodes)
#Connect internet protocol stack to all networks including
#CSMA, station wifi and ap wifi nodes, they shoudl all support
#standard internet protocols

address = ns.internet.Ipv4AddressHelper()
# #Create an IPv4 address helper object to assit ipv4 address to
# #network interfaces
# address.SetBase(ns.network.Ipv4Address("10.1.1.0"), ns.network.Ipv4Mask("255.255.255.0"))
# #Applied ipv4 address and subnet mask (for p2p)
# p2pInterfaces = address.Assign(p2pDevices)
# #Connect address to p2p2 interface(devices), the method is assign



# address.SetBase(ns.network.Ipv4Address("10.1.2.0"), ns.network.Ipv4Mask("255.255.255.0"))
# #Set the base IPv4 address and subnet mask (for CSMA)
# csmaInterfaces = address.Assign(csmaDevices)
# #Connect address to csma interfaces (devices), the method is assign

address.SetBase(ns.network.Ipv4Address("10.1.3.0"), ns.network.Ipv4Mask("255.255.255.0"))
#Ser the base IPv4 address and subnet mask(for wifi)
stainterface=address.Assign(staDevices)
#connect address to station wifi interfaces(decvies)
apinterface=address.Assign(apDevices)

##connect address to access point wifi interfaces(decvies)


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



echoClient1 = ns.applications.UdpEchoClientHelper(serveraddr,9)
#Create a UDP echo client helper object, sending packets to
#IPv4 address from CSMA interfaces at index 'ncsma.value' and on port 9

echoClient1.SetAttribute("MaxPackets", ns.core.UintegerValue(5))
#Configure the maximum number of packets that UDP echo client
#will send to the servers, it is 1 here
echoClient1.SetAttribute("Interval", ns.core.TimeValue(ns.core.Seconds(1.0)))
#Configure time interval between two packets, it is 1.0s
echoClient1.SetAttribute("PacketSize", ns.core.UintegerValue(1024))
#Configure every packet size as 1024 bytes
clientApps1 = echoClient1.Install(wifiStaNodes.Get(1))
#Connect UDP echo client application to wifi node with index
#nwifi.value-1 since it started from 0
clientApps1.Start(ns.core.Seconds(2.0))
#Time to start client application at 2.0s
clientApps1.Stop(ns.core.Seconds(10.0))
#Time to stop client application at 10.0s





echoServer = ns.applications.UdpEchoServerHelper(9)
#Create UDP echo server helper object to listen on port 9
serverApps = echoServer.Install(wifiStaNodes.Get(3))
#Connect a UDP echo server application to CSMA node with index
# vlaue=predefined 3
serverApps.Start(ns.core.Seconds(1.0))
#Time to start server application at 1.0s
serverApps.Stop(ns.core.Seconds(10.0))
#Time to stop server application at 10.0s



ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()
#This is important bcause this program is building a real network
#It calls population routing table method of ipv4 global routing helper
#This line is serving for populating global ipv4 routing tables, which
#is important for proper routing in ns-3
ns.core.Simulator.Stop(ns.core.Seconds(10.0))
#Simulation steops at 10.0s

if tracing.value:
#This section only execute if tracing is enabled
    phy.SetPcapDataLinkType(phy.DLT_IEEE802_11_RADIO)
    #Set packet capture data link type for wifi physical layer
    #to IEEE 802.11 in standard format
    # pointToPoint.EnablePcapAll("draft")
    #It enable tracing for p2p devices, 'thirdis output file name

    phy.EnablePcap("draft", apDevices.Get(0))
    #It enable Pcap tracing for wifi physical layer of ap devices

    # csma.EnablePcap("thirdpy", csmaDevices.Get(0), True)
    #It enables for CSMA devices tracing

   

ns.core.Simulator.Run()
#Advancing simulation clock and executing schduled events
ns.core.Simulator.Destroy()
#Clean up and destoy the simulatin environment, and releasing allocated resources.



