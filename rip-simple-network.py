'''
"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2016 Universita' di Firenze, Italy
 *
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
 * Author: Tommaso Pecorella <tommaso.pecorella@unifi.it>
 */

// Network topology
//
//    SRC
//     |<=== source network
//     A-----B
//      \   / \   all networks have cost 1, except
//       \ /  |   for the direct link from C to D, which
//        C  /    has cost 10
//        | /
//        |/
//        D
//        |<=== target network
//       DST
//
//
// A, B, C and D are RIPng routers.
// A and D are configured with static addresses.
// SRC and DST will exchange packets.
//
// After about 3 seconds, the topology is built, and Echo Reply will be received.
// After 40 seconds, the link between B and D will break, causing a route failure.
// After 44 seconds from the failure, the routers will recovery from the failure.
// Split Horizoning should affect the recovery time, but it is not. See the manual
// for an explanation of this effect.
//
// If "showPings" is enabled, the user will see:
// 1) if the ping has been acknowledged
// 2) if a Destination Unreachable has been received by the sender
// 3) nothing, when the Echo Request has been received by the destination but
//    the Echo Reply is unable to reach the sender.
// Examining the .pcap files with Wireshark can confirm this effect.
'''
import ns3
import ns.core
import ns.internet
import ns.csma
import ns.internet_apps
import sys


def TearDownLink(nodeA,nodeB,interfaceA,interfaceB):
    nodeA.GetObject(ns.internet.Ipv4.GetTypeId()).SetDown(interfaceA)
    nodeB.GetObject(ns.internet.Ipv4.GetTypeId()).SetDown(interfaceB)

cmd = ns.core.CommandLine()
cmd.verbose = "False"
cmd.printRoutingTables = "False"
cmd.showPings = "False"
cmd.SplitHorizon = "PoisonReverse"
cmd.AddValue("verbose", "turn on log components")
cmd.AddValue("printRoutingTables", "Print routing tables at 30, 60 and 90 seconds")
cmd.AddValue("showPings", "Show Ping6 reception")
cmd.AddValue("SplitHorizon", "Split Horizon strategy to use (NoSplitHorizon, SplitHorizon, PoisonReverse)")
verbose = "False"
SplitHorizon = "PoisonReverse"
printRoutingTables = "False"
showPings = False

if verbose=="True":
	ns.core.LogComponentEnableAll(ns.core.LogLevel(ns.core.LOG_PREFIX_TIME | ns.core.LOG_PREFIX_NODE ))
	ns.core.LogComponentEnable("RipSimpleRouting", ns.core.LOG_LEVEL_INFO)
	ns.core.LogComponentEnable("Rip", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable("Ipv4Interface", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable("Icmpv4L4Protocol", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable("Ipv4L3Protocol", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable("ArpCache", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable("V4Ping", ns.core.LOG_LEVEL_ALL)

if SplitHorizon == "NoSplitHorizon":
	ns.core.Config.SetDefault ("ns3::Rip::SplitHorizon", ns.core.EnumValue (ns.internet.RipNg.NO_SPLIT_HORIZON))
elif SplitHorizon=="SplitHorizon":
    ns.core.Config.SetDefault ("ns3::Rip::SplitHorizon", ns.core.EnumValue (ns.internet.RipNg.SPLIT_HORIZON))
else:
	ns.core.Config.SetDefault ("ns3::Rip::SplitHorizon", ns.core.EnumValue (ns.internet.RipNg.POISON_REVERSE))

print "Create nodes."
Names = ns.core.Names()
src = ns.network.Node()
Names.Add("SrcNode",src)
dst = ns.network.Node()
Names.Add("DstNode",dst)
a = ns.network.Node()
Names.Add("RouterA",a)
b = ns.network.Node()
Names.Add("RouterB",b)
c = ns.network.Node()
Names.Add("RouterC",c)
d = ns.network.Node()
Names.Add("RouterD",d)
Net1 = ns.network.NodeContainer()
Net1.Add(src)
Net1.Add(a)
Net2 = ns.network.NodeContainer()
Net2.Add(a)
Net2.Add(b)
Net3 = ns.network.NodeContainer()
Net3.Add(a)
Net3.Add(c)
Net4 = ns.network.NodeContainer()
Net4.Add(b)
Net4.Add(c)
Net5 = ns.network.NodeContainer()
Net5.Add(c)
Net5.Add(d)
Net6 = ns.network.NodeContainer()
Net6.Add(b)
Net6.Add(d)
Net7 = ns.network.NodeContainer()
Net7.Add(b)
Net7.Add(dst)
routers = ns.network.NodeContainer()
routers.Add(a)
routers.Add(b)
routers.Add(c)
routers.Add(d)
nodes = ns.network.NodeContainer()
nodes.Add(src)
nodes.Add(dst)

print "Create channels."
csma = ns.csma.CsmaHelper()
csma.SetChannelAttribute ("DataRate", ns.core.StringValue('5000000'))
csma.SetChannelAttribute ("Delay", ns.core.StringValue('0.02'))
ndc1 = ns.network.NetDeviceContainer()
ndc1 = csma.Install(Net1)
ndc2 = ns.network.NetDeviceContainer()
ndc2 = csma.Install(Net2)
ndc3 = ns.network.NetDeviceContainer()
ndc3 = csma.Install(Net3)
ndc4 = ns.network.NetDeviceContainer()
ndc4 = csma.Install(Net4)
ndc5 = ns.network.NetDeviceContainer()
ndc5 = csma.Install(Net5)
ndc6 = ns.network.NetDeviceContainer()
ndc6 = csma.Install(Net6)
ndc7 = ns.network.NetDeviceContainer()
ndc7 = csma.Install(Net7)

print "Create IPv4 and routing"
ripRouting = ns.internet.RipHelper()

#Rule of thumb:
#Interfaces are added sequentially, starting from 0
#However, interface 0 is always the loopback...

ripRouting.ExcludeInterface (a, 1)
ripRouting.ExcludeInterface (d, 3)

ripRouting.SetInterfaceMetric (c, 3, 10)
ripRouting.SetInterfaceMetric (d, 1, 10)

listRH = ns.internet.Ipv4ListRoutingHelper()
listRH.Add (ripRouting, 0);

'''
//  Ipv4StaticRoutingHelper staticRh;
//  listRH.Add (staticRh, 5);
'''

internet = ns.internet.InternetStackHelper()
internet.SetIpv6StackInstall(False)
internet.SetRoutingHelper(listRH)
internet.Install(routers)

internetNodes = ns.internet.InternetStackHelper()
internetNodes.SetIpv6StackInstall(False)
internetNodes.Install(nodes)

#Assign addresses.
#The source and destination networks have global addresses
#The "core" network just needs link-local addresses for routing.
#We assign global addresses to the routers as well to receive
#ICMPv6 errors.

print "Assign IPv4 Addresses."
ipv4 = ns.internet.Ipv4AddressHelper()

ipv4.SetBase(ns.network.Ipv4Address("10.0.0.0"), ns.network.Ipv4Mask("255.255.255.0"))
#iic1 = ipv4.InterfaceContainer()
iic1 = ipv4.Assign(ndc1)

ipv4.SetBase(ns.network.Ipv4Address("10.0.1.0"), ns.network.Ipv4Mask("255.255.255.0"))
#iic2 = Ipv4.InterfaceContainer()
iic2 = ipv4.Assign(ndc2)

ipv4.SetBase(ns.network.Ipv4Address("10.0.2.0"), ns.network.Ipv4Mask("255.255.255.0"))
#iic3 = Ipv4.InterfaceContainer()
iic3 = ipv4.Assign(ndc3)

ipv4.SetBase(ns.network.Ipv4Address("10.0.3.0"), ns.network.Ipv4Mask("255.255.255.0"))
#iic4 = Ipv4.InterfaceContainer()
iic4 = ipv4.Assign(ndc4)

ipv4.SetBase(ns.network.Ipv4Address("10.0.4.0"), ns.network.Ipv4Mask("255.255.255.0"))
#iic5 = Ipv4.InterfaceContainer()
iic5 = ipv4.Assign(ndc5)

ipv4.SetBase(ns.network.Ipv4Address("10.0.5.0"), ns.network.Ipv4Mask("255.255.255.0"))
#iic6 = Ipv4.InterfaceContainer()
iic6 = ipv4.Assign(ndc6)

ipv4.SetBase(ns.network.Ipv4Address("10.0.6.0"), ns.network.Ipv4Mask("255.255.255.0"))
#iic7 = Ipv4.InterfaceContainer() 
iic7 = ipv4.Assign(ndc7)

'''
staticRouting = Ptr(Ipv4StaticRouting)
staticRouting = Ipv4RoutingHelper::GetRouting <Ipv4StaticRouting> (src->GetObject<Ipv4> ()->GetRoutingProtocol ());
staticRouting->SetDefaultRoute ("10.0.0.2", 1 );
staticRouting = Ipv4RoutingHelper::GetRouting <Ipv4StaticRouting> (dst->GetObject<Ipv4> ()->GetRoutingProtocol ());
staticRouting->SetDefaultRoute ("10.0.6.1", 1 );
'''

if printRoutingTables=="True":
	routingHelper = ns.internet.RipHelper() 

	routingStream = Ptr(OutputStreamWrapper)  
	#routingStream = Create(OutputStreamWrapper ,&std::cout)

	routingHelper.PrintRoutingTableAt(ns.core.Seconds(30.0), a, routingStream)
	routingHelper.PrintRoutingTableAt(ns.core.Seconds(30.0), b, routingStream)
	routingHelper.PrintRoutingTableAt(ns.core.Seconds(30.0), c, routingStream)
	routingHelper.PrintRoutingTableAt(ns.core.Seconds(30.0), d, routingStream)

	routingHelper.PrintRoutingTableAt(ns.core.Seconds(60.0), a, routingStream)
	routingHelper.PrintRoutingTableAt(ns.core.Seconds(60.0), b, routingStream)
	routingHelper.PrintRoutingTableAt(ns.core.Seconds(60.0), c, routingStream)
	routingHelper.PrintRoutingTableAt(ns.core.Seconds(60.0), d, routingStream)

	routingHelper.PrintRoutingTableAt(ns.core.Seconds(90.0), a, routingStream)
	routingHelper.PrintRoutingTableAt(ns.core.Seconds(90.0), b, routingStream)
	routingHelper.PrintRoutingTableAt(ns.core.Seconds(90.0), c, routingStream)
	routingHelper.PrintRoutingTableAt(ns.core.Seconds(90.0), d, routingStream)

print "Create Applications."
#packetSize = ns.core.uint32_t() 
packetSize = 1024
interPacketInterval = ns.core.Time() 
interPacketInterval = ns.core.Seconds(1.0)
ping = ns.internet_apps.V4PingHelper(ns.network.Ipv4Address("10.0.6.2"))  

ping.SetAttribute("Interval", ns.core.TimeValue(interPacketInterval))
ping.SetAttribute("Size", ns.core.UintegerValue(packetSize))
if showPings=="True":
	ping.SetAttribute("Verbose", ns.core.BooleanValue(true))
apps = ns.network.ApplicationContainer() 
apps = ping.Install(src)
apps.Start(ns.core.Seconds(1.0))
apps.Stop(ns.core.Seconds(110.0))


ascii = ns.network.AsciiTraceHelper()
csma.EnableAsciiAll(ascii.CreateFileStream("rip-simple-routing.tr"))
csma.EnablePcapAll("rip-simple-routing", True)

ns.core.Simulator.Schedule(ns.core.Seconds(40), TearDownLink(b, d, 3, 4))

#Now, do the actual simulation.

print "Run Simulation."
ns.core.Simulator.Stop(ns.core.Seconds(131.0))
ns.core.Simulator.Run()
ns.core.Simulator.Destroy()
print "Done."
