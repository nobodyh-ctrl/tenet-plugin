---
name: networking-lab
description: Teach networking (TCP/IP, subnetting, DNS, routing, switching, VLANs, NAT, firewalls) with diagrams, commands, exercises and controlled labs on local VMs, containers or simulators. Use when the user is learning or troubleshooting networking concepts.
argument-hint: "[topic]"
---

# Networking lab

## Rules
- Labs run on networks the learner controls: Docker networks, VMs, network namespaces, Packet Tracer or GNS3, Containerlab.
- No scanning or traffic generation against third-party networks.

## Steps
1. **Diagnostic.** Place the learner on the layers (L2, L3, L4, L7), addressing and subnetting, DNS and routing basics.
2. **Explain with a diagram.**
   - Draw the topology in Mermaid or ASCII, with addresses, VLANs and gateways.
   - Walk one packet end to end: ARP, routing decision, NAT, DNS resolution.
3. **Show the observation commands** for the learner's OS:

   | Purpose | Linux / macOS | Windows |
   |---|---|---|
   | Addresses and routes | `ip a`, `ip r` | `ipconfig /all`, `route print` |
   | Neighbors | `ip neigh` | `arp -a` |
   | Sockets | `ss -tulpn` | `netstat -ano` |
   | DNS | `dig`, `nslookup` | `Resolve-DnsName` |
   | Path and reachability | `traceroute`, `tracepath` | `Test-NetConnection` |
   | Packet capture | `tcpdump`, Wireshark | Wireshark |

4. **Exercise.** Give subnetting, routing-table or troubleshooting scenarios with expected answers.
5. **Lab.** Build the topology with `/forge:hands-on-lab`, for example two Docker networks joined by a router container with NAT. Validate with ping, traceroute and captures. Clean up.
6. **Checkpoint.** The learner predicts a packet's path or a command's output before running it.

## Verification
- The topology diagram matches the lab configuration.
- Every lab step has its expected output, and validation used real commands.
- Cleanup removed the lab networks and containers or VMs.
