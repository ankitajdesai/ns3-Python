# * -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*
# *
# * Copyright (c) 2015 - Chip Webb
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License version 2 as
# * published by the Free Software Foundation;
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# *
# * Author: Chip Webb  <ns3 (at) chipwebb.com>
# *
# *

#// ###################################################################### //
#//                         Network topology                               //
#// ---------------------------------------------------------------------- //
#//                                                                        //
#// This example shows two L2 LANs connected by a WAN link and illustrates //
#// a network that has multiple L2 switches between L3 routers.            //
#//                                                                        //
#// It serves as a test case to verify a patch to global-router-interface  //
#// that fixes a previous bug (#2102 in the ns-3 tracker) but is also      //
#// another example program.                                               //
#//                                                                        //
#// The LANs are "top" [192.168.1/24] and "bottom" [192.168.2/24].         //
#// Each LAN network is interconnected by several L2 switches, and each    //
#// LAN has its own router to act as a gateway with the WAN. Each LAN      //
#// has two endpoints upon which is installed a UDP echo client or server  //
#// that are used to test connectivity over the LANs & WAN.                //
#//                                                                        //
#// One pair of UDP endpoints (t3 and b3) have LAN connections with only   //
#// one switch between them and their local routers. This path works with  //
#// unpatched ns3 code (3.24 & earlier) as well as with the patch applied. //
#//                                                                        //
#// Another pair of endpoints (t2 and b2) have LAN connections with        //
#// a chain of multiple switches between them and their local router.      //
#// This path will only work after applying the associated patch.          //
#//                                                                        //
#// The LAN links are modeled by half-duplex Ethernet CSMA links which     //
#// have command-line-configurable data rate and latency.                  //
#//                                                                        //
#// There are two types of CSMA links: 100Mbit and 10Mbit. The 100Mbit     //
#// links are called csmaX, are denoted by [X] in the diagram and can      //
#// be controlled with the --csmaXRate and --csmaXDelay command line args. //
#// The 10Mbit links are called csmaY, are denoted by [Y] in the diagram   //
#// and can be controlled with the --csmaYRate and --csmaYDelay command    //
#// line arguments. Both the top and bottom LAN have a mixture of          //
#// 100Mbit/s and 10Mbit/s links.                                          //
#//                                                                        //
#// The WAN is modeled by a point-to-point link which has configurable     //
#// data rate and latency. Unlike many typical home/work networks,         //
#// the routers do not perform NAT.                                        //
#//                                                                        //
#// The WAN link is denoted by [P] in the diagram, and the                 //
#// speed and latency can be set from the command line with the            //
#// --p2pRate and --p2pDelay options. The default for this link is 5Mbit/s //
#// and 50ms delay                                                         //
#//                                                                        //
#// Note: Names in parenthesis after NetDevices are pcap tap locations.    //
#//                                                                        //
#// ---------------------------------------------------------------------- //
#//                                                                        //
#//   192.168.  192.168.                                                   //
#//    .1.2      .1.3                                                      //
#//  ---------  ---------                                                  //
#//  |  t2   |  |  t3   |                                                  //
#//  |  UDP  |  |  UDP  |                                                  //
#//  |  echo |  |  echo |    Node t2 is a UDP echo client (multi-switch)   //
#//  | client|  | server|    Node t3 is a UDP echo server (single-switch)  //
#//  ---------  ---------                                                  //
#//   CSMA(t2)   CSMA(t3)                                                  //
#//     [X]        [X]                                                     //
#//     [X]        [X]                                                     //
#//    CSMA        [X]                                                     //
#//  ---------     [X]                                                     //
#//  |  ts4  |     [X]        Nodes ts1, ts2, ts3 and ts4 are L2 switches  //
#//  |  (sw) |     [X]        The top LAN is subnet 192.168.1.*            //
#//  ---------     [X]                                                     //
#//    CSMA        [X]        The long chain of switches is designed       //
#//     [Y]        [X]        to test whether global-router-interface      //
#//     [Y]        [X]        can fully enumerate an IP subnet that has    //
#//    CSMA        [X]        multiple interconnected L2 switches.         //
#//  ---------     [X]        The problem is documented in Bug #2102.      //
#//  |  ts3  |     [X]                                                     //
#//  |  (sw) |     [X]                                                     //
#//  ---------     [X]                                                     //
#//    CSMA        [X]                                                     //
#//     [X]        [X]                                                     //
#//     [X]        [X]                                                     //
#//    CSMA        [X]                                                     //
#//  ---------     [X]                                                     //
#//  |  ts2  |     [X]                                                     //
#//  |  (sw) |     [X]                                                     //
#//  ---------     [X]                                                     //
#//    CSMA        [X]                                                     //
#//     [Y]        [X]                                                     //
#//     [Y]        [X]                                                     //
#//    CSMA       CSMA                                                     //
#//   ------------------                                                   //
#//   |  ts1 (switch)  |                                                   //
#//   ------------------                                                   //
#//          CSMA                                                          //
#//           [Y]                                                          //
#//           [Y]                                                          //
#//          CSMA(trlan)    192.168.1.1                                    //
#//   ------------------                                                   //
#//   |  tr (router)   |    Node tr is an L3 router                        //
#//   ------------------      (between 192.168.1.* & 76.1.1.*)             //
#//           P2P(trwan)    76.1.1.1                                       //
#//           [P]                                                          //
#//           [P]                                                          //
#//           [P]                                                          //
#//           [P]                                                          //
#//           [P]           The WAN is 76.1.1.*                            //
#//           [P]                                                          //
#//           [P]                                                          //
#//           [P]                                                          //
#//           P2P(brwan)    76.1.1.2                                       //
#//   ------------------                                                   //
#//   |  br (router)   |    Node br is an L3 router                        //
#//   ------------------      (between 192.168.2.* & 76.1.1.*)             //
#//          CSMA(brlan)    192.168.2.1                                    //
#//           [X]                                                          //
#//           [X]                                                          //
#//          CSMA                                                          //
#//   ------------------     Nodes bs1 to bs5 are L2 switches              //
#//   |  bs1 (switch)  |     The bottom LAN is subnet 192.168.2.*          //
#//   ------------------                                                   //
#//    CSMA       CSMA                                                     //
#//     [Y]        [Y]                                                     //
#//     [Y]        [Y]                                                     //
#//    CSMA        [Y]                                                     //
#//  ---------     [Y]                                                     //
#//  | bs2   |     [Y]                                                     //
#//  | (sw)  |     [Y]                                                     //
#//  ---------     [Y]                                                     //
#//    CSMA        [Y]                                                     //
#//     [X]        [Y]                                                     //
#//     [X]        [Y]                                                     //
#//    CSMA        [Y]                                                     //
#//  ---------     [Y]                                                     //
#//  | bs3   |     [Y]                                                     //
#//  | (sw)  |     [Y]                                                     //
#//  ---------     [Y]                                                     //
#//    CSMA        [Y]                                                     //
#//     [Y]        [Y]                                                     //
#//     [Y]        [Y]                                                     //
#//    CSMA        [Y]                                                     //
#//  ---------     [Y]                                                     //
#//  | bs4   |     [Y]                                                     //
#//  | (sw)  |     [Y]                                                     //
#//  ---------     [Y]                                                     //
#//    CSMA        [Y]                                                     //
#//     [X]        [Y]                                                     //
#//     [X]        [Y]                                                     //
#//    CSMA        [Y]                                                     //
#//  ---------     [Y]                                                     //
#//  | bs5   |     [Y]                                                     //
#//  | (sw)  |     [Y]                                                     //
#//  ---------     [Y]                                                     //
#//    CSMA        [Y]                                                     //
#//     [Y]        [Y]                                                     //
#//     [Y]        [Y]                                                     //
#//    CSMA(b2)   CSMA(b3)                                                 //
#//  ---------  ---------                                                  //
#//  |  b2   |  |  b3   |                                                  //
#//  |  UDP  |  |  UDP  |                                                  //
#//  |  echo |  |  echo |    Node b2 is a UDP echo server (multi-switch)   //
#//  | server|  | client|    Node b3 is a UDP echo client (single-switch)  //
#//  ---------  ---------                                                  //
#//   192.168.  192.168.                                                   //
#//    .2.2      .2.3                                                      //
#//                                                                        //
#// ---------------------------------------------------------------------- //
#//                            Explanation                                 //
#// ---------------------------------------------------------------------- //
#//                                                                        //
#// UDP packet flows are configured between nodes on the top and bottom    //
#// LANs (using UDP echo client & server).                                 //
#//                                                                        //
#// The network carrying the "multi switch" UDP flow is connected with     //
#// multiple L2 switches between L3 nodes so it should only work if the    //
#// global-router-interface source code properly supports bridging.        //
#//                                                                        //
#// The network carrying the "single switch" UDP flow is connected with    //
#// only one L2 switch between L3 nodes so it should work with or          //
#// without the patch                                                      //
#//                                                                        //
#// = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =  //
#// Traffic summary:                                                       //
#// ---------------------------------------------------------------------- //
#//                                                                        //
#// - UDP flow  from t2 (192.168.1.2) to b2 (192.168.2.2) [Multi Switch]   //
#//             from b3 (192.168.2.3) to t3 (192.168.1.3) [Single Switch]  //
#//                                                                        //
#// = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =  //
#// Node List & IP addresses assigned during simulation                    //
#// ---------------------------------------------------------------------- //
#//      t2     : 192.168.1.2 : Top multi-switch UDP echo client           //
#//      t3     : 192.168.1.3 : Top single-switch UDP echo server          //
#//             :                                                          //
#//      ts1    : <no IP>     : Top switch 1 (bridge)                      //
#//      ts2    : <no IP>     : Top switch 2 (bridge)                      //
#//      ts3    : <no IP>     : Top switch 3 (bridge)                      //
#//      ts4    : <no IP>     : Top switch 4 (bridge)                      //
#//             :                                                          //
#//      tr     : 192.168.1.1 : Router connecting top LAN (192.168.1.*)    //
#//             : 76.1.1.1    :                to the WAN                  //
#//             :                                                          //
#//      br     : 76.1.1.2    : Router connecting the WAN                  //
#//             : 192.168.2.1 :                to bot LAN (192.168.2.*)    //
#//             :                                                          //
#//      bs1    : <no IP>     : Bottom switch 1 (bridge)                   //
#//      bs2    : <no IP>     : Bottom switch 2 (bridge)                   //
#//      bs3    : <no IP>     : Bottom switch 3 (bridge)                   //
#//      bs4    : <no IP>     : Bottom switch 4 (bridge)                   //
#//      bs5    : <no IP>     : Bottom switch 5 (bridge)                   //
#//             :                                                          //
#//      b2     : 192.168.2.2 : Bottom multi-switch UDP echo server        //
#//      b3     : 192.168.2.3 : Bottom single-switch UDP echo client       //
#//             :                                                          //
#// ---------------------------------------------------------------------- //
#// Author:     Chip Webb <ns3 (a) chipwebb dot com>                       
# // ###################################################################### 

#Porting to python is done as an assignment work by 
#    Hindustani Modi
#    Karan Shah
#    Ronak Ginodiya
#    Mohit Mavani
#and mentor by Ms. Ankita J. Desai of C. G. Patel Institute of Technology, Bardoli.

import ns.core
import ns.internet_apps
import ns.csma
import ns.internet
import ns.network
import ns.point_to_point
import ns.bridge
import ns.applications
import sys

def vssearch(loc, vec):
	if(loc in vec):
		return True
verbose = "True"
simDurationSeconds = 60.0
enableUdpMultiSW = 'true'
enableUdpSingleSW = 'true'

csmaXLinkDataRate    = "100Mbps"
csmaXLinkDelay       = "500ms"

csmaYLinkDataRate    = "10Mbps"
csmaYLinkDelay       = "500ms"

pcapLocations        = ""
snapLen              = ns.network.PcapFile.SNAPLEN_DEFAULT

p2pLinkDataRate      = "5Mbps"
p2pLinkDelay         = "50ms"

udpEchoPort          = 9        # // The well-known UDP echo port 

#  // ----------------------------------------------------------------------
#  // Create command line options and get them
#  // ----------------------------------------------------------------------

cmd = ns.core.CommandLine()

cmd.Usage    ("NOTE: valid --pcap arguments are: 't2,t3,b2,b3,trlan,trwan,brlan,brwan'")

cmd.AddValue ("verbose",      "Enable printing informational messages",        verbose);

cmd.AddValue ("duration",     "Duration of simulation.",                       str(simDurationSeconds));

cmd.AddValue ("udpMultiSW",   "Enable udp over multi-switch links",            enableUdpMultiSW)

cmd.AddValue ("udpSingleSW",  "Enable udp over single-switch links",           enableUdpSingleSW)

cmd.AddValue ("pcap",         "Comma separated list of PCAP Locations to tap", pcapLocations)

cmd.AddValue ("snapLen",      "PCAP packet capture length",                    str(snapLen));

cmd.AddValue ("csmaXRate",    "CSMA X Link data rate",                         csmaXLinkDataRate);

cmd.AddValue ("csmaXDelay",   "CSMA X Link delay",                             csmaXLinkDelay);

cmd.AddValue ("csmaYRate",    "CSMA Y Link data rate",                         csmaYLinkDataRate);

cmd.AddValue ("csmaYDelay",   "CSMA Y Link delay",                             csmaYLinkDelay);

cmd.AddValue ("p2pRate",      "P2P Link data rate",                            p2pLinkDataRate);

cmd.AddValue ("p2pDelay",     "P2P Link delay",                                p2pLinkDelay);

cmd.Parse(sys.argv)

# --------------------------------------------------------------------
# Users may find it convenient to turn on explicit debugging
# for selected modules; the below lines suggest how to do this
# --------------------------------------------------------------------

if verbose == "True":
	ns.core.LogComponentEnable("GlobalRouter", ns.core.LOG_LEVEL_INFO)


# ======================================================================
# Define the list of valid PCAP taps
# ----------------------------------------------------------------------

pcapTaps = []
pcapTaps.append ("t2")              # multi-switch  UDP echo client
pcapTaps.append ("t3")              # single-switch UDP echo server
pcapTaps.append ("b2")              # multi-switch  UDP echo server
pcapTaps.append ("b3")              # single-switch UDP echo client
pcapTaps.append ("trlan")           # top router    LAN side
pcapTaps.append ("trwan")           # top router    WAN side
pcapTaps.append ("brlan")           # bottom router LAN side
pcapTaps.append ("brwan")           # bottom router WAN side

# ----------------------------------------------------------------------
# Parse the pcapLocations string into pcapLocationVec
# ----------------------------------------------------------------------

pcapLocationVec = []
if (pcapLocations != "" ):
	sStream = pcapLocations.split(',')
	for substr in sStream:
		if (vssearch (substr,pcapTaps)):
        		pcapLocationVec.append ( substr )
          	else:
	        	print "WARNING: Unrecognized PCAP location: < %s >"%substr
	for ch in pcapLocationVec:
		print "PCAP capture at: < %s >"%ch
		

#  // ======================================================================
#  // Set some simulator-wide values
#  // ======================================================================
#  // ----------------------------------------------------------------------
#  // Set PCAP packet capture maximum packet length
#  // ----------------------------------------------------------------------

if (snapLen != ns.network.PcapFile.SNAPLEN_DEFAULT):
      ns.core.Config.SetDefault ("ns.network.PcapFileWrapper.CaptureSize",   ns.core.UintegerValue (snapLen))

#  // ======================================================================
#  // Create the nodes & links required for the topology shown in comments above.
#  // ----------------------------------------------------------------------

print "INFO: Create nodes."    # // - - - - - - - - - - - - - - - -
                               # // Node IP     : Description
                               # // - - - - - - - - - - - - - - - -
t2  = ns.network.Node()        # // 192.168.1.2 : Top multi-switch udp echo client
t3  = ns.network.Node()        # // 192.168.1.3 : Top single-switch   udp echo server
                               # //             :
ts1 = ns.network.Node()        # // <no IP>     : Top switch #1 (bridge)
ts2 = ns.network.Node()        # // <no IP>     : Top switch #2 (bridge)
ts3 = ns.network.Node()        # // <no IP>     : Top switch #3 (bridge)
ts4 = ns.network.Node()        # // <no IP>     : Top switch #4 (bridge)
                               # //             :
tr  = ns.network.Node()        # // 192.168.1.1 : Router connecting top LAN & WAN
                               # // 76.1.1.1    :
                               # //             :
br  = ns.network.Node()        # // 76.1.1.2    : Router connecting WAN & bottom LANs
                               # // 192.168.2.1 :
                               # //             :
bs1 = ns.network.Node()        # // <no IP>     : Bottom switch #1 (bridge)
bs2 = ns.network.Node()        # // <no IP>     : Bottom switch #2 (bridge)
bs3 = ns.network.Node()        # // <no IP>     : Bottom switch #3 (bridge)
bs4 = ns.network.Node()        # // <no IP>     : Bottom switch #4 (bridge)
bs5 = ns.network.Node()        # // <no IP>     : Bottom switch #5 (bridge)
                               # //             :
b2  = ns.network.Node()        # // 192.168.2.2 : Bottom multi-switch udp echo server

b3  = ns.network.Node()        # // 192.168.2.3 : Bottom single-switch   udp echo client
                               # // - - - - - - - - - - - - - - - -

#  // ----------------------------------------------------------------------
#  // Give the nodes names
#  // ----------------------------------------------------------------------

Names = ns.core.Names()

Names.Add('t2', t2)
Names.Add('t3', t3)
Names.Add('ts1',ts1)
Names.Add('ts2',ts2)
Names.Add('ts3',ts3)
Names.Add('ts4',ts4)
Names.Add('tr', tr)
Names.Add('br', br)
Names.Add('bs1',bs1)
Names.Add('bs2',bs2)
Names.Add('bs3',bs3)
Names.Add('bs4',bs4)
Names.Add('bs5',bs5)
Names.Add('b2', b2)
Names.Add('b3', b3)

#  // ======================================================================
#  // Create CSMA links to use for connecting LAN nodes together
#  // ----------------------------------------------------------------------
#
#  // ----------------------------------------
#  // CSMA [X]
#  // ----------------------------------------

print ('L2: Create a %s %s CSMA link for csmaX for LANs.'%(csmaXLinkDataRate, csmaXLinkDelay))

csmaX = ns.csma.CsmaHelper()

csmaX.SetChannelAttribute("DataRate", ns.core.StringValue(csmaXLinkDataRate))
csmaX.SetChannelAttribute("Delay", ns.core.StringValue(csmaXLinkDelay))

#  // ----------------------------------------
#  // CSMA [Y]
#  // ----------------------------------------
  
print ('L2: Create a %s %s CSMA link for csmaY for LANs.'%(csmaYLinkDataRate, csmaYLinkDelay))

csmaY = ns.csma.CsmaHelper()

csmaY.SetChannelAttribute("DataRate", ns.core.StringValue(csmaYLinkDataRate))
csmaY.SetChannelAttribute("Delay", ns.core.StringValue(csmaXLinkDelay))

#  // ----------------------------------------------------------------------
#  // Now, connect the top LAN nodes together with csma links.
#  // ----------------------------------------------------------------------

print 'L2: Connect nodes on top LAN together with half-duplex CSMA links.'

#  // Multi-switch top LAN chain: t2-ts4-ts3-ts2-ts1-tr
Net1 = ns.network.NodeContainer()
Net1.Add(t2)
Net1.Add(ts4)

link_t2_ts4 = csmaX.Install(Net1)

Net2 = ns.network.NodeContainer()
Net2.Add(ts4)
Net2.Add(ts3)

link_ts4_ts3 = csmaY.Install(Net2)

Net3 = ns.network.NodeContainer()
Net3.Add(ts3)
Net3.Add(ts2)

link_ts3_ts2 = csmaX.Install(Net3)

Net4 = ns.network.NodeContainer()
Net4.Add(ts2)
Net4.Add(ts1)

link_ts2_ts1 = csmaY.Install(Net4)

#  // Single-switch top LAN link: t3-ts1-tr
Net5 = ns.network.NodeContainer()
Net5.Add(t3)
Net5.Add(ts1)

link_t3_ts1 = csmaX.Install(Net5)

#  // Common link for top LAN between ts1 and tr (for t2 and t3 to get to tr)
Net6 = ns.network.NodeContainer()
Net6.Add(tr)
Net6.Add(ts1)

link_tr_ts1 = csmaY.Install(Net6)

#  // ----------------------------------------------------------------------
#  // And repeat above steps to connect the bottom LAN nodes together
#  // ----------------------------------------------------------------------

print 'L2: Connect nodes on bottom LAN together with half-duplex CSMA links.'

#  // Multi-switch bottom LAN chain: b2-bs5-bs4-bs3-bs2-bs1-br
Netb1 = ns.network.NodeContainer()
Netb1.Add(b2)
Netb1.Add(bs5)

link_b2_bs5 = csmaY.Install(Netb1)

Netb2 = ns.network.NodeContainer()
Netb2.Add(bs5)
Netb2.Add(bs4)

link_bs5_bs4 = csmaX.Install(Netb2)

Netb3 = ns.network.NodeContainer()
Netb3.Add(bs4)
Netb3.Add(bs3)

link_bs4_bs3 = csmaY.Install(Netb3)

Netb4 = ns.network.NodeContainer()
Netb4.Add(bs3)
Netb4.Add(bs2)

link_bs3_bs2 = csmaX.Install(Netb4)

Netb5 = ns.network.NodeContainer()
Netb5.Add(bs2)
Netb5.Add(bs1)

link_bs2_bs1 = csmaY.Install(Netb5)

# // Single-switch bottom LAN link: b3-bs1-br
Netb6 = ns.network.NodeContainer()
Netb6.Add(b3)
Netb6.Add(bs1)

link_b3_bs1 = csmaY.Install(Netb6)

# // Common link for bottom LAN between bs1 and br (for b2 and b3 to get to br)
Netb7 = ns.network.NodeContainer()
Netb7.Add(br)
Netb7.Add(bs1)

link_br_bs1 = csmaX.Install(Netb7)

#  // ======================================================================
#  // Create a point-to-point link for connecting WAN nodes together
#  // (this type of link is full-duplex)
#  // ----------------------------------------------------------------------
  
print ('L2: Create a %s %s Point-to-Point link for the WAN.'%(p2pLinkDataRate, p2pLinkDelay))

p2p = ns.point_to_point.PointToPointHelper()

p2p.SetDeviceAttribute("DataRate", ns.core.StringValue(p2pLinkDataRate))
p2p.SetChannelAttribute("Delay", ns.core.StringValue(p2pLinkDelay))

#  // ----------------------------------------------------------------------
#  // Now, connect top router to bottom router with a p2p WAN link
#  // ----------------------------------------------------------------------
  
print 'L2: Connect the routers together with the Point-to-Point WAN link.'

Netp2p = ns.network.NodeContainer()
Netp2p.Add(tr)
Netp2p.Add(br)

link_tr_br = p2p.Install(Netp2p)

#  // ======================================================================
#  // Manually create the list of NetDevices for each switch
#  // ----------------------------------------------------------------------

#  // Top Switch 4 NetDevices
ts4nd = ns.network.NetDeviceContainer()
ts4nd.Add(link_t2_ts4.Get(1));
ts4nd.Add(link_ts4_ts3.Get(0));

#  // Top Switch 3 NetDevices
ts3nd = ns.network.NetDeviceContainer()
ts3nd.Add(link_ts4_ts3.Get(1));
ts3nd.Add(link_ts3_ts2.Get(0));

#  // Top Switch 2 NetDevices
ts2nd = ns.network.NetDeviceContainer()
ts2nd.Add(link_ts3_ts2.Get(1));
ts2nd.Add(link_ts2_ts1.Get(0));

#  // Top Switch 1 NetDevices
ts1nd = ns.network.NetDeviceContainer()
ts1nd.Add(link_ts2_ts1.Get(1));
ts1nd.Add(link_t3_ts1.Get(1));
ts1nd.Add(link_tr_ts1.Get(1));

#  // Bottom Switch 2 NetDevices
bs1nd = ns.network.NetDeviceContainer()
bs1nd.Add(link_br_bs1.Get(1));
bs1nd.Add(link_bs2_bs1.Get(1));
bs1nd.Add(link_b3_bs1.Get(1));

#  // Bottom Switch 3 NetDevices
bs2nd = ns.network.NetDeviceContainer()
bs2nd.Add(link_bs2_bs1.Get(0));
bs2nd.Add(link_bs3_bs2.Get(1));

#  // Bottom Switch 4 NetDevices
bs3nd = ns.network.NetDeviceContainer()
bs3nd.Add(link_bs3_bs2.Get(0));
bs3nd.Add(link_bs4_bs3.Get(1));

#  // Bottom Switch 5 NetDevices
bs4nd = ns.network.NetDeviceContainer()
bs4nd.Add(link_bs4_bs3.Get(0));
bs4nd.Add(link_bs5_bs4.Get(1));

#  // Bottom Switch 5 NetDevices
bs5nd = ns.network.NetDeviceContainer()
bs5nd.Add(link_bs5_bs4.Get(0));
bs5nd.Add(link_b2_bs5.Get(1));

#  // ======================================================================
#  // Install bridging code on each switch
#  // ----------------------------------------------------------------------

bridge = ns.bridge.BridgeHelper()

bridge.Install('ts1', ts1nd)
bridge.Install('ts2', ts2nd)
bridge.Install('ts3', ts3nd)
bridge.Install('ts4', ts4nd)

bridge.Install('bs1', bs1nd)
bridge.Install('bs2', bs2nd)
bridge.Install('bs3', bs3nd)
bridge.Install('bs4', bs4nd)
bridge.Install('bs5', bs5nd)

#  // ======================================================================
#  // Install the L3 internet stack  (TCP/IP)
#  // ----------------------------------------------------------------------

ns3IpStack = ns.internet.InternetStackHelper()

#  // ----------------------------------------------------------------------
#  // Install the L3 internet stack on UDP endpoints
#  // ----------------------------------------------------------------------

print 'L3: Install the ns3 IP stack on udp client and server nodes.'

endpointNodes = ns.network.NodeContainer()
endpointNodes.Add(t2)
endpointNodes.Add(t3)
endpointNodes.Add(b2)
endpointNodes.Add(b3)

ns3IpStack.Install(endpointNodes)

#  // ----------------------------------------------------------------------
#  // Install the L3 internet stack on routers.
#  // ----------------------------------------------------------------------

print 'L3: Install the ns3 IP stack on routers.'

routerNodes = ns.network.NodeContainer()
routerNodes.Add(tr)
routerNodes.Add(br)
ns3IpStack.Install (routerNodes)
# ======================================================================
# Assign top LAN IP addresses
# ----------------------------------------------------------------------

print "L3: Assign top LAN IP Addresses."

topLanIpDevices = ns.network.NetDeviceContainer()
topLanIpDevices.Add (link_tr_ts1.Get (0))  # NOTE: order matters here
topLanIpDevices.Add (link_t2_ts4.Get (0))  #       for IP address
topLanIpDevices.Add (link_t3_ts1.Get (0))  #       assignment
                     
ipv4 = ns.internet.Ipv4AddressHelper()
ipv4.SetBase(ns.network.Ipv4Address('192.168.1.0'), ns.network.Ipv4Mask('255.255.255.0'))
ipv4.Assign(topLanIpDevices)
# ----------------------------------------------------------------------
# Assign bottom LAN IP addresses
# ----------------------------------------------------------------------

print "L3: Assign bottom LAN IP Addresses."

botLanIpDevices = ns.network.NetDeviceContainer()     	# - - - - - -- - - - - - -
botLanIpDevices.Add (link_br_bs1.Get (0))  		# NOTE: order matters here
botLanIpDevices.Add (link_b2_bs5.Get (0))  		#       for IP address
botLanIpDevices.Add (link_b3_bs1.Get (0))  		#       assignment
                                              		# - - - - - -- - - - - - -

ipv4.SetBase (ns.network.Ipv4Address('192.168.2.0'), ns.network.Ipv4Mask('255.255.255.0'))
ipv4.Assign  (botLanIpDevices)
# ----------------------------------------------------------------------
# Assign WAN IP addresses
# ----------------------------------------------------------------------

print "L3: Assign WAN IP Addresses."

ipv4.SetBase (ns.network.Ipv4Address('76.1.1.0'), ns.network.Ipv4Mask('255.255.255.0'))
ipv4.Assign  (link_tr_br)
# ======================================================================
# Calculate and populate routing tables
# ----------------------------------------------------------------------

print "L3: Populate routing tables."

ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

# ======================================================================
# Multi-Switch UDP traffic generation
# ----------------------------------------------------------------------

apps = ns.network.ApplicationContainer() 

if enableUdpMultiSW :
      # ------------------------------------------------------------------
      # Install multi-switch UDP echo server on b2
      # ------------------------------------------------------------------
      
      print "APP: Multi-Switch UDP server (on node b2 of bottom LAN)"

      server = ns.applications.UdpEchoServerHelper(udpEchoPort)
      serverApp = ns.network.ApplicationContainer(server.Install (b2)) 
      serverApp.Start(ns.core.Seconds(0.5))
      serverApp.Stop(ns.core.Seconds(simDurationSeconds))
      # ------------------------------------------------------------------
      # Install multi-switch UDP echo client on t2
      # ------------------------------------------------------------------
      
      print "APP: Multi-Switch UDP client (on node t2 of top LAN)"

      interPacketInterval = ns.core.Time(ns.core.Seconds (0.005))
      packetSize = 1000
      maxPacketCount = (simDurationSeconds - 2.0) / 0.005
      client =ns.applications.UdpEchoClientHelper (ns.network.Ipv4Address ("192.168.2.2"), udpEchoPort)

      client.SetAttribute ("MaxPackets", ns.core.UintegerValue (int(maxPacketCount)))
      client.SetAttribute ("Interval",   ns.core.TimeValue     (interPacketInterval))
      client.SetAttribute ("PacketSize", ns.core.UintegerValue (packetSize))

      clientApp = ns.network.ApplicationContainer(client.Install (t2))
      clientApp.Start (ns.core.Seconds (0.5))
      clientApp.Stop  (ns.core.Seconds (simDurationSeconds))

# ======================================================================
# Single-Switch UDP traffic generation
#----------------------------------------------------------------------
if enableUdpSingleSW :
	# ------------------------------------------------------------------
      	#Install single-switch UDP echo server on t3
      	# ------------------------------------------------------------------
      	
      	print "APP: Single-Switch UDP server (on node t3 of top LAN)"

       	server = ns.applications.UdpEchoServerHelper(udpEchoPort)

     	serverApp = ns.network.ApplicationContainer(server.Install (t3))
      	serverApp.Start(ns.core.Seconds(0.5))
      	serverApp.Stop(ns.core.Seconds (simDurationSeconds))
	
	# ------------------------------------------------------------------
      	# Install single-switch UDP echo client on b3
      	# ------------------------------------------------------------------
      	
      	print "APP: Single-Switch UDP client (on node b3 bottom LAN)"

      	interPacketInterval = ns.core.Time(ns.core.Seconds (0.005))
      	packetSize = 1000
      	maxPacketCount = (simDurationSeconds - 2.0) / 0.005

       	client = ns.applications.UdpEchoClientHelper (ns.network.Ipv4Address ("192.168.1.3"), udpEchoPort)

      	client.SetAttribute ("MaxPackets", ns.core.UintegerValue (int(maxPacketCount)))
      	client.SetAttribute ("Interval",   ns.core.TimeValue     (interPacketInterval))
      	client.SetAttribute ("PacketSize", ns.core.UintegerValue (packetSize))

      	clientApp = ns.network.ApplicationContainer(client.Install (b3))
      	clientApp.Start (ns.core.Seconds (0.5))
      	clientApp.Stop  (ns.core.Seconds (simDurationSeconds))

# ======================================================================
# Print routing tables at T=0.1
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# NOTE: Node 0 and Node 13 must have non-empty tables (except for local 
#       loopback and local LAN) if routing is operating correctly.
# ----------------------------------------------------------------------

print "Set up to print routing tables at T=0.1s"

routingStream = ns.network.OutputStreamWrapper("global-routing-multi-switch-plus-router.routes", ns.network.STD_IOS_OUT)
g = ns.internet.Ipv4GlobalRoutingHelper()
g.PrintRoutingTableAllAt (ns.core.Seconds (0.1), routingStream)

# ======================================================================
# Configure PCAP traces
# ----------------------------------------------------------------------

print "Configure PCAP Tracing (if any configured)."
 
# - - - - - - - - - - - - - -
# multi-switch UDP echo client
# - - - - - - - - - - - - - -
if vssearch ("t2",pcapLocationVec):
      csmaX.EnablePcap ("t2.pcap",topLanIpDevices.Get (1), True, True)

# - - - - - - - - - - - - - -
# multi-switch UDP echo server
# - - - - - - - - - - - - - -
if vssearch ("b2",pcapLocationVec):
      csmaY.EnablePcap ("b2.pcap",botLanIpDevices.Get (1), True, True)

# - - - - - - - - - - - - - -
# single-switch UDP echo client
# - - - - - - - - - - - - - -
if vssearch ("b3",pcapLocationVec):
      csmaY.EnablePcap ("b3.pcap",botLanIpDevices.Get (2), True, True)

# - - - - - - - - - - - - - -
# single-switch UDP echo server
# - - - - - - - - - - - - - -
if vssearch ("t3",pcapLocationVec):
      csmaX.EnablePcap ("t3.pcap",topLanIpDevices.Get (2), True, True)

# - - - - - - - - - - - - - -
# top router, LAN side
# - - - - - - - - - - - - - -
if vssearch ("trlan",pcapLocationVec):
      csmaY.EnablePcap ("trlan.pcap", topLanIpDevices.Get (0), True, True)

# - - - - - - - - - - - - - -
# bottom router, LAN side
# - - - - - - - - - - - - - -
if vssearch ("brlan",pcapLocationVec):
      csmaX.EnablePcap ("brlan.pcap", botLanIpDevices.Get (0), True, True)

# - - - - - - - - - - - - - -
# top router, WAN side
# - - - - - - - - - - - - - -
if vssearch ("trwan",pcapLocationVec):
      p2p.EnablePcap ("trwan.pcap",link_tr_br.Get (0), True, True)

# - - - - - - - - - - - - - -
# bottom router, WAN side
# - - - - - - - - - - - - - -
if vssearch ("brwan",pcapLocationVec):
      p2p.EnablePcap ("brwan.pcap",  link_tr_br.Get (1), True, True)

# ======================================================================
# Now, do the actual simulation.
# ----------------------------------------------------------------------

print "Run Simulation for %s seconds."%(simDurationSeconds);

ns.core.Simulator.Stop (ns.core.Seconds (simDurationSeconds))
ns.core.Simulator.Run ()
ns.core.Simulator.Destroy ()
print 'Done.'
