# L03/C06/T02 — tcpdump & Wireshark

## Learning Objectives

- Capture packets with tcpdump
- Apply BPF filters precisely
- Analyze captures in Wireshark

## tcpdump Basics

```bash
sudo tcpdump -i eth0                       # capture eth0
sudo tcpdump -i any                        # all interfaces
sudo tcpdump -n -i any                     # no DNS resolution
sudo tcpdump -nn -i any                    # also no service name
sudo tcpdump -vvv -i any                   # very verbose
sudo tcpdump -X -i any                     # hex + ASCII
sudo tcpdump -c 100 -i any                 # 100 packets then stop
sudo tcpdump -s 0 -i any                   # full packet (default truncates)
sudo tcpdump -w capture.pcap -i any        # save to file
sudo tcpdump -r capture.pcap               # read from file
```

## BPF Filters

```bash
sudo tcpdump 'host 1.2.3.4'
sudo tcpdump 'src 1.2.3.4'
sudo tcpdump 'dst 1.2.3.4'
sudo tcpdump 'net 10.0.0.0/8'
sudo tcpdump 'port 443'
sudo tcpdump 'tcp port 443'
sudo tcpdump 'tcp port 443 and host 1.2.3.4'
sudo tcpdump 'src host 1.2.3.4 and dst port 443'
sudo tcpdump 'tcp[tcpflags] & (tcp-syn|tcp-fin) != 0'   # SYN or FIN packets
sudo tcpdump 'tcp[tcpflags] & tcp-rst != 0'             # RST packets
sudo tcpdump 'icmp'
sudo tcpdump 'arp'
sudo tcpdump 'host 1.2.3.4 and not port 22'             # exclude SSH (avoid loop)
```

## Reading Output

```
12:00:00.001234 IP src.host.54321 > dst.host.443: Flags [S], seq 1000, win 65535, length 0
```

- Timestamp
- L3 protocol (IP)
- Source / destination (with port)
- Flags: `S` SYN, `.` ACK only, `P` PUSH, `F` FIN, `R` RST
- Sequence number
- Window size
- Payload length

## Common Use Cases

### TCP Handshake
```bash
sudo tcpdump -nn -i any 'host 1.2.3.4 and port 443'
```

Look for: SYN, SYN-ACK, ACK sequence at start; FIN/RST at end.

### Investigate Resets
```bash
sudo tcpdump -nn -i any 'tcp[tcpflags] & tcp-rst != 0'
```

Find who sends RST.

### DNS Queries
```bash
sudo tcpdump -nn -i any -X port 53
```

See DNS query + response.

### See HTTP (cleartext)
```bash
sudo tcpdump -nn -A -i any 'tcp port 80'
```

`-A` shows ASCII; HTTP is readable.

## Capture to File for Wireshark

```bash
sudo tcpdump -w capture.pcap -i any 'port 443'
# Stop with Ctrl-C
scp capture.pcap your-laptop:/tmp/    # if on remote
# Open in Wireshark
```

## Wireshark

GUI for analyzing pcap files. Rich filters and dissectors.

### Common Display Filters
```
ip.addr == 1.2.3.4
tcp.port == 443
tcp.flags.reset == 1
tcp.analysis.retransmission
http.request.method == "POST"
http.response.code == 500
tls.handshake.type == 1     # ClientHello
dns.qry.name contains "google"
```

### Follow Stream
Right-click packet → Follow → TCP Stream. Reconstructs application data.

### Statistics
Statistics menu → Conversations, Endpoints, IO Graphs. Visualize traffic patterns.

## Decrypting TLS in Wireshark

```bash
export SSLKEYLOGFILE=/tmp/keys.log
# Run browser; it logs keys
# Open Wireshark; preferences → Protocols → TLS → "(Pre)-Master-Secret log filename" → /tmp/keys.log
# TLS sessions decrypt visibly
```

curl supports too: `curl --tls-keys ...`.

## Common Captures You'll Make

### Web App Slow
```bash
sudo tcpdump -w slow.pcap -i any 'host webserver and port 443'
# Reproduce
# Stop
```
In Wireshark: check TLS handshake time; HTTP response times; retransmits.

### Connection Refused
```bash
sudo tcpdump -nn -i any 'host target and (tcp-syn or icmp)'
```
See if SYN reaches target; if RST returned (port closed) or no response (firewalled).

### Mystery Disconnects
```bash
sudo tcpdump -w drops.pcap -i any 'tcp port 5432'    # whatever port
```
Look for unexpected FINs or RSTs.

## Live Capture Performance

High-traffic captures may drop packets:
```
2 packets dropped by kernel
```

Mitigations:
- Bigger ring buffer: `tcpdump -B 4096`
- Filter early (in BPF, not display)
- Capture less verbose info

## On K8s

### From host
```bash
sudo tcpdump -i any 'host POD_IP'
```

### Pod with no shell
```bash
kubectl debug -it POD --image=nicolaka/netshoot --target=CONTAINER
# Inside: tcpdump
```

netshoot has tcpdump, ngrep, mtr, dig, curl, etc.

## Common Mistakes

- Capturing on loopback interface: `-i lo`
- Forgetting to filter (huge captures fill disk)
- Capturing SSH session while SSH'd in (loop; filter it out)
- Truncated packets (forget `-s 0`)

## Best Practices

- **Filter in BPF, not in Wireshark** — a tight capture filter (`host X and port Y`) keeps files small and avoids dropped packets; display filters only hide, they don't reduce capture load.
- Always **write to a file** (`-w cap.pcap`) for anything non-trivial and analyze offline in Wireshark — terminal output loses detail and timing precision.
- Use **ring buffers** in prod (`-C 100 -W 10 -w cap.pcap`) so a long capture rotates instead of filling the disk.
- **Exclude your own SSH/control traffic** (`and not port 22`) to avoid the capture-of-the-capture feedback loop and noise.
- On Kubernetes, capture with **`kubectl debug --image=nicolaka/netshoot`** sharing the target's network namespace rather than guessing the host interface.
- **Sanitize before sharing** — cleartext HTTP/DNS/auth tokens live in pcaps; scrub or restrict access.

## Quick Refs

```bash
# Capture: all ifaces, no name resolution, full packets, to file
sudo tcpdump -i any -nn -s 0 -w cap.pcap 'host 1.2.3.4 and port 443'

# Rotating ring buffer (10 files × 100 MB)
sudo tcpdump -i any -nn -C 100 -W 10 -w cap.pcap 'port 443'

# Read back, only RST packets
tcpdump -nn -r cap.pcap 'tcp[tcpflags] & tcp-rst != 0'

# K8s: capture in a pod with no shell
kubectl debug -it POD --image=nicolaka/netshoot --target=CONTAINER
```

BPF cheat sheet: `host`/`src`/`dst`, `net 10.0.0.0/8`, `port 443`, `tcp`/`udp`/`icmp`, combine with `and`/`or`/`not`. Flag tests: `tcp[tcpflags] & tcp-syn != 0`, `... & tcp-rst != 0`.

Wireshark display filters: `tcp.flags.reset==1`, `tcp.analysis.retransmission`, `tcp.analysis.zero_window`, `http.response.code>=500`, `tls.handshake.type==1`. tcpdump flags: `S`=SYN `.`=ACK `P`=PUSH `F`=FIN `R`=RST.

## Interview Prep

**Mid**: "Capture TCP handshake with tcpdump."

**Senior**: "Show me how to find TCP RSTs."

**Staff**: "Debug a slow API call via packet capture."

## Next Topic

→ [T03 — netstat, ss, lsof](T03-Netstat-SS.md)
