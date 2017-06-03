/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
    * This program is free software; you can redistribute it and/or modify
        * it under the terms of the GNU General Public License version 2 as
            * published by the Free Software Foundation;
                *
                    * This program is distributed in the hope that it will be useful,
                        * but WITHOUT ANY WARRANTY; without even the implied warranty of
                            * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                                * GNU General Public License for more details.
                                    *
                                        * You should have received a copy of the GNU General Public License
                                            * along with this program; if not, write to the Free Software
                                                * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
                                                    *
                                                        * Contributed by:  Luis Cortes (cortes@gatech.edu)
                                                            */


// This script exercises global routing code in a mixed point-to-point
// and csma/cd environment.  We bring up and down interfaces and observe
// the effect on global routing.  We explicitly enable the attribute
// to respond to interface events, so that routes are recomputed
// automatically.
//
// Network topology
//
//  n0
//     \ p-p
//      \          (shared csma/cd)
//       n2 -------------------------n3
//      /            |        |
//     / p-p        n4        n5 ---------- n6
//   n1                             p-p
//   |                                      |
//   ----------------------------------------
//                p-p
//
// - at time 1 CBR/UDP flow from n1 to n6's IP address on the n5/n6 link
// - at time 10, start similar flow from n1 to n6's address on the n1/n6 link
//
//  Order of events
//  At pre-simulation time, configure global routes.  Shortest path from
//  n1 to n6 is via the direct point-to-point link
//  At time 1s, start CBR traffic flow from n1 to n6
//  At time 2s, set the n1 point-to-point interface to down.  Packets
//    will be diverted to the n1-n2-n5-n6 path
//  At time 4s, re-enable the n1/n6 interface to up.  n1-n6 route restored.
//  At time 6s, set the n6-n1 point-to-point Ipv4 interface to down (note, this
                                                                     //    keeps the point-to-point link "up" from n1's perspective).  Traffic will
                                                                     //    flow through the path n1-n2-n5-n6
                                                                     //  At time 8s, bring the interface back up.  Path n1-n6 is restored
                                                                     //  At time 10s, stop the first flow.
                                                                     //  At time 11s, start a new flow, but to n6's other IP address (the one
                                                                     //    on the n1/n6 p2p link)
//  At time 12s, bring the n1 interface down between n1 and n6.  Packets
//    will be diverted to the alternate path
//  At time 14s, re-enable the n1/n6 interface to up.  This will change 
//    routing back to n1-n6 since the interface up notification will cause
//    a new local interface route, at higher priority than global routing
//  At time 16s, stop the second flow.

// - Tracing of queues and packet receptions to file "dynamic-global-routing.tr"
'''

import ns.core
import ns.network
import ns.csma
import ns.internet
import ns.point_to_point
import ns.applications
import sys
#import ns.ipv4-global-routing-helper

#Allow the user to override any of the defaults and the above
#Bind ()s at run-time, via command-line arguments'''
cmd= ns.internet.CommandLine()
cmd.Parse(sys.argv)

print "Create nodes."
c = ns.network.NodeContainer()
c.Create(7)
n0n2 = NodeContainer (c.Get(0) , c.Get(2))
n1n2 = NodeContainer (c.Get(1) , c.Get(2))
n5n6 = NodeContainer (c.Get(5) , c.Get(6))
n1n6 = NodeContainer (c.Get(1) , c.Get(6))
n2345 = NodeContainer (c.Get(2) , c.Get(3) , c.Get(4) , c.Get(5))

internet = ns.internet.InternetStackHelper()
internet.Install(c)

#We create the channels first without any IP addressing information
print "Create channels.";
p2p = ns.point_to_point.PointToPointHelper()
p2p.SetDeviceAttribute ("DataRate" , ns.core.StringValue("5Mbps"))
p2p.SetChannelAttribute ("Delay" , ns.core.StringValue("2ms"))
d0d2 = p2p.Install (n0n2)
d1d6 = p2p.Install (n1n6)

d1d2 = p2p.Install(n1n2)

#We create the channels first without any IP addressing information
csma = ns.csma.CsmaHelper()
csma.SetChannelAttribute ("DataRate" , ns.core.StringValue("5Mbps"))
csma.SetChannelAttribute ("Delay" , ns.core.StringValue("2ms"))
d2345 = csma.Install (n2345)

#Later, we add IP addresses.
print "Assign IP Addresses."
ipv4 = ns.internet.Ipv4AddressHelper()
ipv4.SetBase (ns.network.Ipv4Address("10.1.1.0"),ns.network.Ipv4Mask("255.255.255.0"))
ipv4.Assign (d0d2)

ipv4.SetBase (ns.network.Ipv4Address("10.1.2.0"),ns.network.Ipv4Mask("255.255.255.0"))
ipv4.Assign (d1d2)

ipv4.SetBase (ns.network.Ipv4Address("10.1.3.0"),ns.network.Ipv4Mask("255.255.255.0"))
i5i6 = ipv4.Assign (d5d6);

ipv4.SetBase (ns.network.Ipv4Address("10.250.1.0"),ns.network.Ipv4Mask("255.255.255.0"))
ipv4.Assign (d2345);

ipv4.SetBase (ns.network.Ipv4Address("172.16.1.0"),ns.network.Ipv4Mask("255.255.255.0"))
i1i6 = ipv4.Assign (d1d6);

#Create router nodes, initialize routing database and set up the routing
#tables in the nodes.

ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

# Create the OnOff application to send UDP datagrams of size
# 210 bytes at a rate of 448 Kb/s

    print "Create Applications."
port = uint16_t (9)  #Discard port (RFC 863)
onoff = ns.applications.OnOffHelper()
onoff.InetSocketAddress ("ns3::UdpSocketFactory",i5i6.GetAddress (1),port)
onoff.SetConstantRate (DataRate ("2kbps"))
onoff.SetAttribute ("PacketSize", ns.core.UintegerValue (50))

apps = onoff.Install (c.Get(1))
apps.Start (ns.Seconds (1.0))
apps.Stop (ns.Seconds (16.0))


#Create a second OnOff application to send UDP datagrams of size 210 bytes at a rate of 448 Kb/s
onoff2 = ns.applications.OnOffHelper()
onoff2.InetSocketAddress (i1i6.GetAddress(1),port)
onoff2.SetAttribute ("OnTime",ns.core.Stringvalue("ns3::ConstantRandomVariable[Constant=1]"))
onoff2.SetAttribute ("OffTime",ns.core.Stringvalue("ns3::ConstantRandomVariable[Constant=1]"))
onoff2.SetAttribute ("DataRate",ns.core.Stringvalue("2kbps"))
onoff2.SetAttribute ("PacketSize",ns.core.UintegerValue(50))

apps2 = onoff2.Install (c.Get(1))
apps2.Start(ns.Seconds (11.0))
aps2.Stop (ns.Seconds (16.0))

#Create an optional packet sink to receive these packets
sink = ns.applications.PacketSinkHelper("ns3::UdpSocketFactory",
                                        ns.network.Address(ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(), port)))
apps = sink.Install(ns.network.NodeContainer(c.Get(6)))
apps.Start (ns.Seconds (1.0))
apps.Stop (ns.Seconds (10.0))

sink2 = ns.applications.PacketSinkHelper("ns3::UdpSocketFactory", ns.network.Address(ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(),port)))
apps2 = sink2.Install(ns.network.NodeContainer(c.Get(6)))

apps2.Start (ns.Seconds (11.0))
apps2.Stop (ns.Seconds (16.0))

ascii = ns.internet.AsciiTraceHelper()

'''stream = (OutputStreamWrapper) ascii.CreateFileStream ("dynamic-global-routing.tr")'''

p2p.EnableAsciiAll (ascii.CreateFileStream ("dynamic-global-routing.tr"))
csma.EnableAsciiAll (ascii.CreateFileStream ("dynamic-global-routing.tr"))
internet.EnableAsciiIpv4All (ascii.CreateFileStream ("dynamic-global-routing.tr"))

p2p.EnablePcapAll ("dynamic-global-routing")
csma.EnablePcapAll ("dynamic-global-routing", False)

'''(Node)n1 = c.Get (1)
(Ipv4)ipv41 = (Ipv4)n1.GetObject()'''

n1 = c.Get(1)
ipv41 = n1.GetObject(ns.network.Ipv4)

#The first ifIndex is 0 for loopback, then the first p2p is numbered 1,
#then the next p2p is numbered 2
'''ipv4ifIndex1 = uint32_t(2)'''

ipv4ifIndex1 = 2
ns.core.Simulator.Schedule (ns.Seconds (6),&Ipv4::SetDown,ipv41, ipv4ifIndex1)
ns.core.Simulator.Schedule (ns.Seconds (4),&Ipv4::SetUp,ipv46, ipvifIndex1)

n6 = c.Get (6);
ipv46 = n6.Ipv4.GetObject()

#The first ifIndex is 0 for loopback, then the first p2p is numbered 1,
#then the next p2p is numbered 2
ipv4ifIndex6 = uint32_t(2)
ns.core.Simulator.Schedule (ns.Seconds (6),&Ipv4::SetDown,ipv46, ipv4ifIndex6)
ns.core.Simulator.Schedule (ns.Seconds (8),&Ipv4::SetUp,ipv46, ipv4ifIndex6)

#Trace routing tables
g = ns.internet.Ipv4GlobalRoutingHelper()
'''(OutputStreamWrapper) routingStream = Create(OutputStreamWrapper) ("dynamic-global-routing.routes", std::ios::out);''''
g.PrintRoutingTableAllAt (ns.Seconds (12), routingStream)

print "Run Simulation."
ns.core.Simulator.Run()
ns.core.Simulator.Destroy()
print "Done."
