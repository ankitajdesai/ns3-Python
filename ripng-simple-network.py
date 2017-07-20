''' /*
# * Copyright (c) 2014 Universita' di Firenze, Italy
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
# * Author: Tommaso Pecorella <tommaso.pecorella@unifi.it>

# // Network topology
# //
# //    SRC
# //     |<=== source network
# //     A-----B
# //      \   / \   all networks have cost 1, except
# //       \ /  |   for the direct link from C to D, which
# //        C  /    has cost 10
# //        | /
# //        |/
# //        D
# //        |<=== target network
# //       DST
# //
# //
# // A, B, C and D are RIPng routers.
# // A and D are configured with static addresses.
# // SRC and DST will exchange packets.
# //
# // After about 3 seconds, the topology is built, and Echo Reply will be received.
# // After 40 seconds, the link between B and D will break, causing a route failure.
# // After 44 seconds from the failure, the routers will recovery from the failure.
# // Split Horizoning should affect the recovery time, but it is not. See the manual
# // for an explanation of this effect.
# //
# // If "showPings" is enabled, the user will see:
# // 1) if the ping has been acknowledged
# // 2) if a Destination Unreachable has been received by the sender
# // 3) nothing, when the Echo Request has been received by the destination but
# //    the Echo Reply is unable to reach the sender.
# // Examining the .pcap files with Wireshark can confirm this effect.*/  '''

import ns.core
import ns.internet
import ns.csma
import ns.internet_apps
import ns.network
import sys

def TearDownLink(nodeA,nodeB,interfaceA,interfaceB):
	nodeA.GetObject(ns.internet.Ipv6.GetTypeId()).SetDown(interfaceA)
	nodeB.GetObject(ns.internet.Ipv6.GetTypeId()).SetDown(interfaceB)

cmd = ns.core.CommandLine()
cmd.verbose = "False"
printRoutingTables = "False"
cmd.showPings = "False"

SplitHorizon=ns.core.StringValue ("PoisonReverse")

cmd.AddValue ("verbose", "turn on log components")
cmd.AddValue ("printRoutingTables", "Print routing tables at 30, 60 and 90 seconds")
cmd.AddValue ("showPings", "Show Ping6 reception")

cmd.Parse (sys.argv)

verbose=cmd.verbose
showPings=cmd.showPings

if verbose == "True":
	ns.core.LogComponentEnable ("RipNgSimpleRouting", ns.core.LOG_LEVEL_INFO)
	ns.core.LogComponentEnable ("RipNg", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable ("Icmpv6L4Protocol", ns.core.LOG_LEVEL_INFO)
	ns.core.LogComponentEnable ("Ipv6Interface", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable ("Icmpv6L4Protocol", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable ("NdiscCache", ns.core.LOG_LEVEL_ALL)
	ns.core.LogComponentEnable ("Ping6Application", ns.core.LOG_LEVEL_ALL)

if showPings == "True":
	ns.core.LogComponentEnable ("Ping6Application", ns.core.LOG_LEVEL_INFO)	

if SplitHorizon == "NoSplitHorizon":
	ns.core.Config.SetDefault ("ns3::RipNg::SplitHorizon", ns.core.EnumValue(ns.internet.RipNg.NO_SPLIT_HORIZON))

elif SplitHorizon == "SplitHorizon":
	ns.core.Config.SetDefault ("ns3::RipNg::SplitHorizon", ns.core.EnumValue(ns.internet.RipNg.SPLIT_HORIZON))

else:
	ns.core.Config.SetDefault ("ns3::RipNg::SplitHorizon", ns.core.EnumValue(ns.internet.RipNg.POISON_REVERSE))
 

#Create Nodes
print "Create nodes"
src = ns.network.Node();
dst = ns.network.Node();
a = ns.network.Node();
b = ns.network.Node();
c = ns.network.Node();
d = ns.network.Node();

net1 = ns.network.NodeContainer();
net1.Add(src);
net1.Add(a);

net2 = ns.network.NodeContainer();
net2.Add(a);
net2.Add(b);

net3 = ns.network.NodeContainer();
net3.Add(a);
net3.Add(c);

net4 = ns.network.NodeContainer();
net4.Add(b);
net4.Add(c);

net5 = ns.network.NodeContainer();
net5.Add(c);
net5.Add(d);

net6 = ns.network.NodeContainer();
net6.Add(b);
net6.Add(d);

net7 = ns.network.NodeContainer();
net7.Add(d);
net7.Add(dst);

routers = ns.network.NodeContainer();
routers.Add(a);
routers.Add(b);
routers.Add(c);
routers.Add(d);

nodes = ns.network.NodeContainer();
nodes.Add(src);
nodes.Add(dst);

#Create channels
csma = ns.csma.CsmaHelper();
csma.SetChannelAttribute ("DataRate", ns.network.DataRateValue (ns.network.DataRate(5000000)));
csma.SetChannelAttribute ("Delay", ns.core.TimeValue (ns.core.MilliSeconds (2)));
ndc1 = csma.Install (net1);
ndc2 = csma.Install (net2);
ndc3 = csma.Install (net3);
ndc4 = csma.Install (net4);
ndc5 = csma.Install (net5);
ndc6 = csma.Install (net6);
ndc7 = csma.Install (net7);

# Create IPv6 and routing
ripNgRouting = ns.internet.RipNgHelper();

ripNgRouting.ExcludeInterface (a, 1);
ripNgRouting.ExcludeInterface (d, 3);

ripNgRouting.SetInterfaceMetric (c, 3, 10);
ripNgRouting.SetInterfaceMetric (d, 1, 10);

listRH=ns.internet.Ipv6ListRoutingHelper();
listRH.Add (ripNgRouting, 0);

staticRh=ns.internet.Ipv6StaticRoutingHelper();
listRH.Add (staticRh, 5);

internetv6 = ns.internet.InternetStackHelper();
internetv6.SetIpv4StackInstall (False);
internetv6.SetRoutingHelper (listRH);
internetv6.Install (routers);


internetv6Nodes = ns.internet.InternetStackHelper();
internetv6Nodes.SetIpv4StackInstall (False);
internetv6Nodes.Install (nodes);

print "Addressing"
ipv6 = ns.internet.Ipv6AddressHelper();

ipv6.SetBase (ns.network.Ipv6Address("2001:1::"), ns.network.Ipv6Prefix(64));
iic1 = ipv6.Assign(ndc1);
iic1.SetForwarding(1, True);
iic1.SetDefaultRouteInAllNodes(1);

ipv6.SetBase (ns.network.Ipv6Address("2001:0:1::"), ns.network.Ipv6Prefix(64));
iic2 = ipv6.Assign (ndc2);
iic2.SetForwarding (0, True);
iic2.SetForwarding (1, True);

ipv6.SetBase (ns.network.Ipv6Address("2001:0:2::"), ns.network.Ipv6Prefix(64));
iic3 = ipv6.Assign (ndc3);
iic3.SetForwarding (0, True);
iic3.SetForwarding (1, True);

ipv6.SetBase (ns.network.Ipv6Address("2001:0:3::"), ns.network.Ipv6Prefix(64));
iic4 = ipv6.Assign (ndc4);
iic4.SetForwarding (0, True);
iic4.SetForwarding (1, True);

ipv6.SetBase (ns.network.Ipv6Address("2001:0:4::"), ns.network.Ipv6Prefix(64));
iic5 = ipv6.Assign (ndc5);
iic5.SetForwarding (0, True);
iic5.SetForwarding (1, True);

ipv6.SetBase (ns.network.Ipv6Address("2001:0:5::"), ns.network.Ipv6Prefix(64));
iic6 = ipv6.Assign (ndc6);
iic6.SetForwarding (0, True);
iic6.SetForwarding (1, True);

ipv6.SetBase (ns.network.Ipv6Address("2001:2::"), ns.network.Ipv6Prefix(64));
iic7 = ipv6.Assign (ndc7);
iic7.SetForwarding (0, True);
iic7.SetDefaultRouteInAllNodes (0);


if (printRoutingTables =="True"):
	routingHelper=ns.internet.RipNgHelper();
	routingStream = ns.network.OutputStreamWrapper (ns.network.STD_COUT)

	routingHelper.PrintRoutingTableAt (ns.core.Seconds (30.0), a, routingStream);
      	routingHelper.PrintRoutingTableAt (ns.core.Seconds (30.0), b, routingStream);
      	routingHelper.PrintRoutingTableAt (ns.core.Seconds (30.0), c, routingStream);
      	routingHelper.PrintRoutingTableAt (ns.core.Seconds (30.0), d, routingStream);

	routingHelper.PrintRoutingTableAt (ns.core.Seconds (60.0), a, routingStream);
      	routingHelper.PrintRoutingTableAt (ns.core.Seconds (60.0), b, routingStream);
      	routingHelper.PrintRoutingTableAt (ns.core.Seconds (60.0), c, routingStream);
      	routingHelper.PrintRoutingTableAt (ns.core.Seconds (60.0), d, routingStream);

      	routingHelper.PrintRoutingTableAt (ns.core.Seconds (90.0), a, routingStream);
      	routingHelper.PrintRoutingTableAt (ns.core.Seconds (90.0), b, routingStream);
      	routingHelper.PrintRoutingTableAt (ns.core.Seconds (90.0), c, routingStream);
      	routingHelper.PrintRoutingTableAt (ns.core.Seconds (90.0), d, routingStream);

print "Application"
packetSize = 1024;
maxPacketCount = 100;
interPacketInterval = ns.core.Seconds(1.0);
ping6 = ns.internet_apps.Ping6Helper();
ping6.SetLocal (iic1.GetAddress (0, 1));
ping6.SetRemote (iic7.GetAddress (1, 1));

ping6.SetAttribute("MaxPackets", ns.core.UintegerValue(maxPacketCount));
ping6.SetAttribute("Interval", ns.core.TimeValue(interPacketInterval));
ping6.SetAttribute("PacketSize", ns.core.UintegerValue(packetSize));

apps = ping6.Install(ns.network.NodeContainer(net1.Get(0)));
apps.Start(ns.core.Seconds(1.0));
apps.Stop(ns.core.Seconds(110.0));

print "Tracing"
ascii = ns.network.AsciiTraceHelper()
csma.EnableAsciiAll(ascii.CreateFileStream("ripng-simple-routing.tr"))
csma.EnablePcapAll("ripng-simple-routing", True)

#Run simulation
ns.core.Simulator.Schedule(ns.core.Seconds(40), TearDownLink, b, d, 3, 2)
ns.core.Simulator.Stop(ns.core.Seconds(120))
ns.core.Simulator.Run()
ns.core.Simulator.Destroy()

#Done
