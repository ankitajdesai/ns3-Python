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



