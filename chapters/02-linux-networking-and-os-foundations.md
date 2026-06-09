# Chapter 2: Linux, Networking & OS Foundations

---

## Why This Chapter Exists

Every container you run is a Linux process. Every Kubernetes pod is a set of Linux processes sharing namespaces. Every HTTP request your Java service handles traverses the kernel's TCP/IP stack. Every file your application reads passes through the virtual filesystem layer. Every cloud instance is a Linux machine.

If you do not understand Linux and networking at the OS level, you are operating production systems by superstition. You will not understand why a container is OOM-killed, why a service cannot bind to port 80, why DNS resolution takes 5 seconds, why TCP connections pile up in `CLOSE_WAIT`, or why your application sees 100% CPU utilization but `top` shows 25%.

This chapter gives you the foundational knowledge that every subsequent chapter assumes. When we discuss containers in Chapter 3, you will already know what namespaces and cgroups are. When we discuss Kubernetes networking in Chapter 4, you will already know how packets are routed between subnets. When we discuss cloud VPCs in Chapter 6, you will already understand NAT, routing tables, and CIDR notation.

---

## 2.1 The Linux Process Model

### What a Process Actually Is

As a Java developer, you know what a thread is. A process is the operating system's unit of execution, and understanding it deeply is essential because everything in production -- your application, your database, your web server, your monitoring agent -- is a Linux process.

A process is a data structure in the kernel that contains:

```
┌──────────────────────────────────────────────────────┐
│                 PROCESS (task_struct)                  │
│                                                        │
│  PID: 42                    (unique process ID)        │
│  PPID: 1                    (parent process ID)        │
│  UID: 1000                  (user who owns it)         │
│  State: RUNNING             (running, sleeping, etc.)  │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ MEMORY MAP                                        │  │
│  │                                                    │  │
│  │  0xFFFFFFFF ┌──────────────┐  ◄── Kernel space    │  │
│  │             │ Kernel memory │      (off-limits to  │  │
│  │             │              │       user process)   │  │
│  │  0xC0000000 ├──────────────┤                      │  │
│  │             │    Stack     │  ◄── Local variables, │  │
│  │             │      │       │      function calls   │  │
│  │             │      ▼       │                      │  │
│  │             │              │                      │  │
│  │             │      ▲       │                      │  │
│  │             │      │       │                      │  │
│  │             │    Heap      │  ◄── malloc, new     │  │
│  │             ├──────────────┤                      │  │
│  │             │    BSS       │  ◄── Uninitialized   │  │
│  │             ├──────────────┤      globals         │  │
│  │             │    Data      │  ◄── Initialized     │  │
│  │             ├──────────────┤      globals         │  │
│  │             │    Text      │  ◄── Machine code    │  │
│  │  0x00000000 └──────────────┘      (read-only)     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
│  FILE DESCRIPTORS:                                     │
│    0 → stdin  (terminal or pipe)                       │
│    1 → stdout (terminal or pipe)                       │
│    2 → stderr (terminal or pipe)                       │
│    3 → /var/log/app.log (opened file)                  │
│    4 → socket(TCP, 10.0.1.5:8080) (network connection)│
│                                                        │
│  SIGNALS: pending signals, signal handlers             │
│  SCHEDULING: priority, CPU affinity, time slice        │
│  CREDENTIALS: UID, GID, capabilities                   │
└──────────────────────────────────────────────────────┘
```

Every process has its own virtual address space. When your Java application allocates memory with `new`, it is allocating within this virtual address space. The kernel maps virtual addresses to physical RAM pages transparently. Two processes can both have a pointer to address `0x7FFF0000`, but they point to different physical memory. This isolation is fundamental -- it is why one process crashing does not corrupt another process's memory.

### Process Lifecycle

```
                    fork()
  Parent Process ──────────────▶ Child Process (copy of parent)
       │                              │
       │                              │ exec() (optional)
       │                              ▼
       │                         New Program
       │                         (replaces child's memory image)
       │                              │
       │                              │ exit()
       │                              ▼
       │                         Zombie State
       │                         (exit code stored, waiting
       │                          for parent to read it)
       │                              │
       │         wait() / waitpid()   │
       │◄─────────────────────────────┘
       │  (parent collects exit code,
       │   kernel reclaims zombie)
       ▼
  Parent continues
```

This matters for production because:

**Zombie processes:** If a parent process forks children but never calls `wait()`, the children become zombies when they exit. Zombies consume a PID and a slot in the process table but no memory or CPU. However, Linux has a finite number of PIDs (default: 32768). A service that leaks zombies will eventually exhaust the PID space, and no new processes can be created on the system. In a Kubernetes pod, this manifests as mysterious failures where new connections cannot be accepted and commands fail with "Cannot fork."

**Orphan processes:** If a parent process exits before its children, the children are re-parented to PID 1 (init/systemd). In containers, PID 1 is whatever command you specified in your Dockerfile's `ENTRYPOINT`. If your entrypoint is a shell script that does not properly handle child processes, orphans accumulate inside the container. This is why production containers often use `tini` or `dumb-init` as PID 1 -- they properly reap child processes.

**The Java connection:** When you run `java -jar app.jar`, the JVM is a single process. JVM threads are Linux threads (lightweight processes created with `clone()` rather than `fork()`). They share the same virtual address space but have separate stacks. When you see "200 threads" in your Java application, the kernel sees 200 schedulable entities sharing one memory space.

### Process States

```
                          ┌─────────────┐
          fork()          │             │
  ───────────────────────▶│   CREATED   │
                          │             │
                          └──────┬──────┘
                                 │ scheduled by kernel
                                 ▼
                ┌──────── RUNNING/RUNNABLE ◄────────┐
                │         (on CPU or in              │
                │          run queue)                 │
                │                │                    │
  waiting for   │                │ waiting for        │ I/O completes
  I/O, lock,    │                │ I/O, lock,         │ or signal
  signal, etc.  │                │ signal, etc.       │ received
                │                ▼                    │
                │     ┌──────────────────┐            │
                │     │    SLEEPING      │────────────┘
                │     │                  │
                │     │ Interruptible:   │
                │     │  waiting for I/O │
                │     │  (most common)   │
                │     │                  │
                │     │ Uninterruptible: │
                │     │  waiting for     │
                │     │  disk/NFS I/O    │
                │     │  (D state --     │
                │     │   cannot be      │
                │     │   killed)        │
                │     └──────────────────┘
                │
                │         exit()
                └────────────────────▶ ZOMBIE ──▶ (reaped by parent)
```

**Why the "D state" matters in production:** A process in uninterruptible sleep (state `D`) is waiting for a disk I/O or NFS operation that has not returned. It cannot be killed, even with `kill -9`. If you see many processes in state `D`, it typically means your disk is saturated, your NFS mount is unresponsive, or there is a kernel-level I/O issue. In a Kubernetes context, pods stuck in `D` state on a node can cause the node to become `NotReady` as the kubelet itself can get stuck.

---

## 2.2 System Calls: The Kernel Boundary

### What System Calls Are

Your Java application runs in user space. The kernel runs in kernel space. System calls are the only way for user-space code to request services from the kernel -- reading files, opening network connections, allocating memory, creating processes.

When your Java application calls `new FileInputStream("/etc/config.yaml")`, deep inside the JVM this translates to:

```
YOUR JAVA CODE
  │
  │  new FileInputStream("/etc/config.yaml")
  ▼
JVM (Java Native Interface)
  │
  │  open("/etc/config.yaml", O_RDONLY)
  ▼
GLIBC (C standard library)
  │
  │  syscall(SYS_openat, AT_FDCWD, "/etc/config.yaml", O_RDONLY)
  ▼
────────────────── USER/KERNEL BOUNDARY (trap/interrupt) ──────────
  │
  ▼
KERNEL
  │
  │  1. Validate file path
  │  2. Check permissions (does this UID have read access?)
  │  3. Walk the directory tree: / → etc → config.yaml
  │  4. Load inode from filesystem
  │  5. Allocate a file descriptor (e.g., fd=3)
  │  6. Return fd to user space
  │
  ▼
────────────────── KERNEL/USER BOUNDARY (return) ──────────────────
  │
  ▼
GLIBC
  │
  │  Returns fd=3
  ▼
JVM
  │
  │  Wraps fd in FileInputStream object
  ▼
YOUR JAVA CODE
  │
  │  FileInputStream is ready to use
```

Every system call involves a **context switch** from user mode to kernel mode. This is not free -- it costs roughly 100-1000 nanoseconds depending on the CPU and the syscall. For a single call, this is negligible. For millions of calls per second (e.g., a high-throughput service doing tiny I/O operations), it can become a measurable performance bottleneck.

### System Calls That Every DevOps Engineer Must Know

| Syscall    | What It Does                           | When You Encounter It                              |
|------------|----------------------------------------|----------------------------------------------------|
| `fork`     | Create a new process (copy of parent)  | Every time a shell runs a command                   |
| `exec`     | Replace current process with new program| Shell runs `java -jar app.jar`                     |
| `open`     | Open a file, return file descriptor    | Every file access, every config read                |
| `read`     | Read bytes from file descriptor        | Reading files, reading from sockets                 |
| `write`    | Write bytes to file descriptor         | Writing logs, sending HTTP responses                |
| `close`    | Close a file descriptor                | Done with a file or connection                      |
| `socket`   | Create a network socket                | Opening a network connection                        |
| `bind`     | Assign address to a socket             | Server listens on port 8080                         |
| `listen`   | Mark socket as accepting connections   | Server starts accepting clients                     |
| `accept`   | Accept incoming connection             | Each new TCP connection                             |
| `connect`  | Initiate a connection to remote        | Client connects to a database                       |
| `mmap`     | Map file or memory into address space  | JVM heap allocation, shared memory                  |
| `brk`      | Change data segment size               | malloc/heap growth                                  |
| `epoll`    | Efficient I/O event notification       | Netty, Nginx, Node.js event loops                   |
| `clone`    | Create thread or process with shared memory | JVM thread creation, container creation         |
| `mount`    | Mount a filesystem                     | Container filesystem setup                          |
| `chroot`   | Change root directory                  | Container filesystem isolation (historical)         |
| `unshare`  | Create new namespaces                  | Container namespace isolation                       |

### Why This Matters for Production Debugging

When your Java service is slow and you cannot figure out why, `strace` lets you see every system call the process makes:

```
$ strace -p 12345 -c -S time
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
 85.21    4.293012         214     20040           futex
  8.73    0.439823          11     40080           epoll_wait
  3.12    0.157234           8     20040           write
  1.89    0.095234           5     20040           read
  0.52    0.026123           3      8016           recvfrom
  0.31    0.015623           2      8016           sendto
  0.22    0.011234           1      8016           close
```

In this trace, 85% of the time is spent in `futex` (fast userspace mutex), which means the application is spending most of its time waiting on locks. This points to thread contention -- perhaps a synchronized block in Java that is too coarse-grained, or a connection pool that is too small, forcing threads to wait for connections.

Without understanding system calls, this output is meaningless. With understanding, it is a roadmap to the performance problem.

---

## 2.3 The Linux Filesystem Hierarchy

### Why You Need to Know This

Every Linux system -- every EC2 instance, every container, every Kubernetes node -- follows the same directory structure. When you SSH into a production machine to debug an issue, you need to know where to look.

```
/
├── bin/          Essential user binaries (ls, cp, cat, bash)
│                 Needed for single-user mode and boot
│
├── sbin/         Essential system binaries (mount, iptables, ip)
│                 Needed for boot and system repair
│
├── etc/          System-wide configuration files
│                 /etc/hosts          ← local DNS overrides
│                 /etc/resolv.conf    ← DNS server configuration
│                 /etc/passwd         ← user accounts
│                 /etc/shadow         ← password hashes
│                 /etc/fstab          ← filesystem mount table
│                 /etc/nginx/         ← nginx configuration
│                 /etc/systemd/       ← systemd unit files
│
├── var/          Variable data (changes during operation)
│   ├── log/      System and application logs
│   │             /var/log/syslog     ← system log
│   │             /var/log/auth.log   ← authentication log
│   │             /var/log/kern.log   ← kernel log
│   ├── lib/      State data for applications
│   │             /var/lib/docker/    ← Docker images and containers
│   │             /var/lib/kubelet/   ← Kubelet state
│   └── run/      Runtime data (PIDs, sockets)
│                 /var/run/docker.sock ← Docker API socket
│
├── proc/         Virtual filesystem -- live kernel data
│                 /proc/cpuinfo       ← CPU information
│                 /proc/meminfo       ← Memory statistics
│                 /proc/[pid]/status  ← Process details
│                 /proc/[pid]/fd/     ← Open file descriptors
│                 /proc/[pid]/cgroup  ← Cgroup membership
│                 /proc/[pid]/ns/     ← Namespace references
│
├── sys/          Virtual filesystem -- kernel subsystems
│                 /sys/fs/cgroup/     ← Cgroup controls
│                 /sys/class/net/     ← Network interfaces
│                 /sys/block/         ← Block devices
│
├── tmp/          Temporary files (often tmpfs, backed by RAM)
│
├── home/         User home directories
│
├── root/         Root user's home directory
│
├── opt/          Optional/third-party software
│
├── usr/          User programs and data (read-only)
│   ├── bin/      Non-essential user binaries
│   ├── lib/      Libraries
│   └── local/    Locally compiled software
│
├── dev/          Device files
│                 /dev/null      ← discards all writes
│                 /dev/zero      ← infinite stream of zeroes
│                 /dev/random    ← cryptographic random data
│                 /dev/sda       ← first disk
│
└── mnt/          Temporary mount points
    └── mount/    Additional mount points
```

### /proc -- Your Production Debugging Goldmine

`/proc` is not a real filesystem. It does not exist on disk. It is a virtual filesystem that the kernel creates on the fly, exposing live system state as files. This is how tools like `top`, `ps`, `free`, and `netstat` get their data -- they read from `/proc`.

Critical `/proc` entries for production debugging:

```
/proc/meminfo
  MemTotal:       16384000 kB    ← Total physical RAM
  MemFree:         1234567 kB    ← Completely unused RAM
  MemAvailable:    8765432 kB    ← RAM available for allocation
                                    (includes reclaimable cache)
  Buffers:          234567 kB    ← Disk buffer cache
  Cached:          5678901 kB    ← Page cache (file reads)
  SwapTotal:       4096000 kB    ← Swap space size
  SwapFree:        4096000 kB    ← Swap space unused
```

**A common misunderstanding:** New engineers see low `MemFree` and think the system is out of memory. It is not. Linux aggressively uses free RAM as page cache (caching file data in memory). `MemAvailable` is the correct metric -- it tells you how much memory is actually available for new allocations because the kernel can reclaim cache pages when needed.

```
/proc/[pid]/limits
  Max open files    1024    65536    ← soft/hard limits
```

**Production relevance:** The default open file limit on most Linux distributions is 1024. A single Java service handling thousands of concurrent connections can easily exceed this. Each TCP connection is a file descriptor. Each open file is a file descriptor. Hitting this limit causes `java.net.SocketException: Too many open files`. The fix is increasing the limit in `/etc/security/limits.conf` or in the systemd unit file, but you need to understand the problem to diagnose it.

---

## 2.4 Sockets and the TCP/IP Stack

### What a Socket Is

A socket is a file descriptor that represents one endpoint of a network connection. When your Java application calls `new ServerSocket(8080)`, the kernel creates a socket data structure and returns a file descriptor. The application reads from and writes to this file descriptor just like a file, but the data travels over the network instead of to disk.

### The TCP/IP Model

The TCP/IP stack is layered. Each layer adds its own header and passes the data to the next layer down:

```
YOUR JAVA APPLICATION
  │
  │  "Hello, World!" (application data)
  ▼
┌─────────────────────────────────────────────────────────┐
│  APPLICATION LAYER (HTTP, gRPC, DNS, SMTP)               │
│                                                           │
│  Adds HTTP headers:                                      │
│  HTTP/1.1 200 OK\r\n                                    │
│  Content-Length: 13\r\n                                  │
│  \r\n                                                    │
│  Hello, World!                                           │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│  TRANSPORT LAYER (TCP or UDP)                            │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │ TCP Header (20 bytes)           │ HTTP Data      │    │
│  │                                 │                │    │
│  │ Source Port: 45678              │ HTTP/1.1 200   │    │
│  │ Dest Port:   80                 │ OK\r\n...      │    │
│  │ Seq Number:  1001               │ Hello, World!  │    │
│  │ Ack Number:  5001               │                │    │
│  │ Flags: ACK, PSH                 │                │    │
│  │ Window Size: 65535              │                │    │
│  └──────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│  NETWORK LAYER (IP)                                      │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │ IP Header (20 bytes)  │ TCP Header │ HTTP Data   │    │
│  │                       │            │             │    │
│  │ Source IP: 10.0.1.5   │            │             │    │
│  │ Dest IP:   10.0.2.10  │            │             │    │
│  │ TTL: 64               │            │             │    │
│  │ Protocol: TCP (6)     │            │             │    │
│  └──────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│  LINK LAYER (Ethernet, Wi-Fi)                            │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Eth Header │ IP Header │ TCP Header │ HTTP Data  │    │
│  │            │           │            │            │    │
│  │ Src MAC    │           │            │            │    │
│  │ Dst MAC    │           │            │            │    │
│  │ Type: IPv4 │           │            │            │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
│  Transmitted as electrical signals or light pulses        │
└─────────────────────────────────────────────────────────┘
```

### The TCP Three-Way Handshake (Deep)

Before any HTTP data is exchanged, TCP must establish a connection. This is the handshake that happens every time your Java application opens a new database connection or HTTP client connection:

```
Client (10.0.1.5:45678)                    Server (10.0.2.10:8080)
       │                                          │
       │                                          │  Server calls listen()
       │                                          │  Socket in LISTEN state
       │                                          │
       │──── SYN (seq=1000) ──────────────────▶  │
       │     "I want to connect.                  │
       │      My starting sequence number         │  Server receives SYN
       │      is 1000."                           │  Socket → SYN_RECEIVED
       │                                          │
       │                                          │
       │  ◀── SYN-ACK (seq=5000, ack=1001) ─────│
       │      "OK. My starting sequence           │
       │       number is 5000.                    │
       │       I acknowledge your 1000            │
       │       (expecting 1001 next)."            │
       │                                          │
  Client receives                                 │
  SYN-ACK                                        │
  Socket → ESTABLISHED                            │
       │                                          │
       │──── ACK (seq=1001, ack=5001) ────────▶  │
       │     "I acknowledge your 5000             │
       │      (expecting 5001 next)."             │  Server socket →
       │                                          │  ESTABLISHED
       │                                          │
       │  ◀════ Connection Established ═══════▶  │
       │       (Data can now flow)                │
```

**Why this matters for production:**

1. **SYN floods:** An attacker sends millions of SYN packets but never completes the handshake. The server allocates resources for each half-open connection, eventually exhausting memory. This is a classic DDoS attack. Mitigation: SYN cookies (the kernel encodes connection state in the SYN-ACK sequence number instead of storing it).

2. **Connection latency:** Every new TCP connection requires a round trip (SYN → SYN-ACK → ACK) before data can flow. If your server is in us-east-1 and the client is in ap-southeast-1 (100ms round trip), that is 100ms wasted before the first byte of HTTP data. This is why connection pooling matters -- your Java `DataSource` reuses database connections instead of creating new ones for each query.

3. **The backlog queue:** When the server calls `listen(fd, backlog)`, the `backlog` parameter controls how many completed connections can wait before the application calls `accept()`. If your Java application is slow to accept connections (e.g., all threads are busy), the backlog fills up, and new connections are dropped. The kernel drops them silently -- the client sees a timeout, and there is no error log on the server.

### TCP Connection Teardown

```
Client                                            Server
  │                                                  │
  │──── FIN (seq=2000) ──────────────────────────▶  │
  │     "I'm done sending."                         │
  │     Client → FIN_WAIT_1                          │
  │                                                  │
  │  ◀── ACK (ack=2001) ────────────────────────────│
  │      Client → FIN_WAIT_2                         │  Server can still
  │      (waiting for server's FIN)                  │  send data
  │                                                  │
  │  ◀── FIN (seq=6000) ────────────────────────────│
  │      "I'm done sending too."                     │  Server → LAST_ACK
  │                                                  │
  │──── ACK (ack=6001) ──────────────────────────▶  │
  │     Client → TIME_WAIT                           │  Server → CLOSED
  │     (waits 2 × MSL ≈ 60s)                       │
  │                                                  │
  │     Client → CLOSED                              │
```

**Production problems from TCP teardown:**

**TIME_WAIT accumulation:** After closing a connection, the client enters `TIME_WAIT` for ~60 seconds (2x Maximum Segment Lifetime). During this time, the source port is reserved. A service that rapidly opens and closes connections (e.g., a Java application making many short-lived HTTP calls without connection pooling) can exhaust the ephemeral port range (typically 32768-60999 = ~28,000 ports). Once exhausted, no new outgoing connections can be created, and the application throws `java.net.BindException: Address already in use`.

Diagnosis:
```
$ ss -s
TCP:   28421 (estab 156, closed 0, orphaned 0, timewait 28201)
```

28,201 connections in TIME_WAIT -- this server is about to run out of ephemeral ports.

Fixes:
- Use connection pooling (reuse connections instead of creating new ones)
- Enable `SO_REUSEADDR` / `SO_REUSEPORT`
- Tune `net.ipv4.tcp_tw_reuse = 1` (allows reuse of TIME_WAIT sockets for new outgoing connections)

**CLOSE_WAIT accumulation:** A socket in `CLOSE_WAIT` means the remote side has closed its end of the connection, but the local application has not called `close()`. This is a bug in your application -- you are leaking connections. In Java, this typically means a `Socket` or `HttpURLConnection` that is not closed in a `finally` block (or not using try-with-resources).

```
$ ss -s
TCP:   5421 (estab 156, closed 0, orphaned 0, closewait 5200)
```

5,200 connections in CLOSE_WAIT: your application has a connection leak. The connections will never be cleaned up until the process exits.

---

## 2.5 DNS Resolution Flow

### How DNS Actually Works

When your Java application calls `new URL("https://api.payments.com/charge").openConnection()`, the JVM must resolve `api.payments.com` to an IP address. This process is more complex than most developers realize and is a frequent source of production issues.

```
Your Java Application
  │
  │  InetAddress.getByName("api.payments.com")
  ▼
JVM DNS Cache
  │  Check: is "api.payments.com" in the JVM's internal cache?
  │
  │  YES → return cached IP (JVM caches DNS by default,
  │         often for 30 seconds or forever in some JDK versions)
  │  NO  → continue
  ▼
/etc/nsswitch.conf
  │  Determines resolution order.
  │  Typical config: "hosts: files dns"
  │  Meaning: check /etc/hosts first, then DNS servers
  ▼
/etc/hosts
  │  Check: is there an entry for "api.payments.com"?
  │
  │  127.0.0.1    localhost
  │  10.0.1.100   api.payments.com    ← if present, return this
  │
  │  Not found → continue
  ▼
/etc/resolv.conf
  │  Contains the DNS server(s) to query:
  │
  │  nameserver 10.0.0.2       ← Primary DNS (e.g., VPC DNS in AWS)
  │  nameserver 10.0.0.3       ← Secondary DNS
  │  search svc.cluster.local cluster.local  ← search domains
  │
  ▼
Local DNS Resolver (10.0.0.2)
  │
  │  Check local cache. Not found → recursive resolution.
  ▼
Root DNS Server (one of 13 root server clusters)
  │
  │  Q: "Where is api.payments.com?"
  │  A: "I don't know, but .com is handled by these servers:
  │      a.gtld-servers.net (192.5.6.30)
  │      b.gtld-servers.net (192.33.14.30) ..."
  ▼
.com TLD Server (a.gtld-servers.net)
  │
  │  Q: "Where is api.payments.com?"
  │  A: "I don't know, but payments.com is handled by:
  │      ns1.payments.com (198.51.100.1)
  │      ns2.payments.com (198.51.100.2)"
  ▼
Authoritative DNS Server (ns1.payments.com)
  │
  │  Q: "Where is api.payments.com?"
  │  A: "api.payments.com → 203.0.113.50  (TTL: 300 seconds)"
  ▼
Local DNS Resolver
  │  Caches the result for 300 seconds (the TTL)
  │  Returns 203.0.113.50 to the application
  ▼
Your Java Application
  │  Now knows that api.payments.com = 203.0.113.50
  │  Can open a TCP connection to 203.0.113.50:443
```

### DNS Problems in Production

**Problem 1: JVM DNS Caching**

The JVM caches DNS lookups aggressively. In older JDK versions with a security manager, positive lookups were cached forever. This means if a service IP changes (e.g., AWS ELB IP rotation, failover to a new database), your Java application continues connecting to the old IP.

```
TTL=300 in DNS record
  BUT
JVM caches for:
  - 30 seconds (default with no security manager)
  - Forever (default WITH security manager)
  - Configurable via: networkaddress.cache.ttl in java.security
    or sun.net.inetaddr.ttl system property
```

If your application connects to an AWS RDS database through a DNS endpoint and RDS performs a failover, the DNS record changes to point to the new primary. If the JVM has cached the old IP, your application keeps trying to connect to the old (now standby) instance and fails.

Fix: Set `networkaddress.cache.ttl=60` in your JVM properties.

**Problem 2: DNS in Kubernetes**

Kubernetes DNS resolution adds the search domains from `/etc/resolv.conf`:

```
# Inside a Kubernetes pod:
nameserver 10.96.0.10
search default.svc.cluster.local svc.cluster.local cluster.local
ndots: 5
```

The `ndots: 5` setting means: if the hostname has fewer than 5 dots, try appending each search domain before querying the name as-is.

When your pod resolves `api.payments.com` (2 dots, less than 5):
1. Query `api.payments.com.default.svc.cluster.local` → NXDOMAIN
2. Query `api.payments.com.svc.cluster.local` → NXDOMAIN
3. Query `api.payments.com.cluster.local` → NXDOMAIN
4. Query `api.payments.com` → 203.0.113.50 (finally!)

That is 4 DNS queries instead of 1. At high throughput, this multiplies DNS traffic by 4x and adds latency to every external service call.

Fix: Use a trailing dot: `api.payments.com.` (the dot makes it a fully qualified domain name, skipping search domain expansion). Or set `ndots: 2` if your services do not use deeply nested Kubernetes DNS names.

**Problem 3: DNS TTL and Failover**

When you set a low DNS TTL (e.g., 30 seconds) for fast failover, you trade reliability for DNS query volume. Every 30 seconds, every client must re-resolve the name. For a service with 10,000 clients, that is 333 DNS queries per second just for one domain name. If the DNS server is overwhelmed, resolution fails, and all 10,000 clients lose connectivity -- a DNS-induced outage.

---

## 2.6 The HTTP/HTTPS Handshake and TLS Internals

### What Happens When Your Browser Hits https://api.example.com

This is the full sequence of events from the moment a connection is initiated to the first byte of application data:

```
Client                                              Server
  │                                                    │
  │  ┌──────────── DNS Resolution ─────────────────┐  │
  │  │ Resolve api.example.com → 203.0.113.50      │  │
  │  └──────────── (~50ms with cache miss) ────────┘  │
  │                                                    │
  │  ┌──────────── TCP Handshake ──────────────────┐  │
  │  │ SYN → SYN-ACK → ACK                        │  │
  │  └──────────── (1 RTT, ~20ms) ────────────────┘  │
  │                                                    │
  │  ┌──────────── TLS 1.3 Handshake ─────────────┐  │
  │  │                                              │  │
  │  │─── ClientHello ────────────────────────────▶│  │
  │  │    Supported TLS versions: [1.3, 1.2]       │  │
  │  │    Supported cipher suites:                  │  │
  │  │      TLS_AES_256_GCM_SHA384                 │  │
  │  │      TLS_CHACHA20_POLY1305_SHA256           │  │
  │  │    Key share: (client's ECDH public key)    │  │
  │  │    SNI: api.example.com                     │  │
  │  │                                              │  │
  │  │◀── ServerHello ────────────────────────────│  │
  │  │    Chosen TLS version: 1.3                  │  │
  │  │    Chosen cipher: TLS_AES_256_GCM_SHA384    │  │
  │  │    Key share: (server's ECDH public key)    │  │
  │  │                                              │  │
  │  │◀── Certificate ────────────────────────────│  │
  │  │    Server's X.509 certificate               │  │
  │  │    Contains: server's public key,           │  │
  │  │    domain name, issuer, validity dates      │  │
  │  │                                              │  │
  │  │◀── CertificateVerify ──────────────────────│  │
  │  │    Proves the server owns the private key   │  │
  │  │    matching the certificate                 │  │
  │  │                                              │  │
  │  │◀── Finished ───────────────────────────────│  │
  │  │    Server's handshake authentication tag     │  │
  │  │                                              │  │
  │  │    [Client validates certificate chain:      │  │
  │  │     1. Is the certificate expired?           │  │
  │  │     2. Is the domain name correct?           │  │
  │  │     3. Is the issuer trusted (in CA store)?  │  │
  │  │     4. Is the certificate revoked (OCSP)?]   │  │
  │  │                                              │  │
  │  │─── Finished ────────────────────────────▶  │  │
  │  │    Client's handshake authentication tag     │  │
  │  │                                              │  │
  │  └──────────── (1 RTT for TLS 1.3) ──────────┘  │
  │                                                    │
  │  ┌──────────── Encrypted HTTP Request ─────────┐  │
  │  │                                              │  │
  │  │─── GET /charge HTTP/1.1 ──────────────────▶│  │
  │  │    Host: api.example.com                    │  │
  │  │    (encrypted with symmetric key derived    │  │
  │  │     from ECDH key exchange)                 │  │
  │  │                                              │  │
  │  └─────────────────────────────────────────────┘  │
```

### TLS Deep Dive: What Actually Happens During Key Exchange

The critical innovation in TLS is that two parties who have never communicated before can establish an encrypted channel without ever sending the encryption key over the network. Here is how:

```
CLIENT                                        SERVER
  │                                              │
  │  Generate ephemeral key pair:                │
  │    client_private = random()                 │
  │    client_public = G × client_private        │
  │    (elliptic curve point multiplication)     │
  │                                              │
  │──── client_public ──────────────────────▶   │
  │                                              │
  │                    Generate ephemeral key pair:
  │                      server_private = random()
  │                      server_public = G × server_private
  │                                              │
  │   ◀──── server_public ──────────────────────│
  │                                              │
  │  Both sides compute:                         │
  │                                              │
  │  shared_secret =                             │  shared_secret =
  │    server_public × client_private            │    client_public × server_private
  │                                              │
  │  (These produce the same value due to        │
  │   the mathematical properties of             │
  │   elliptic curve Diffie-Hellman)             │
  │                                              │
  │  Derive symmetric keys from shared_secret:   │
  │    encryption_key = HKDF(shared_secret)      │
  │    mac_key = HKDF(shared_secret)             │
  │                                              │
  │  ◀═══════ All further traffic encrypted ════▶│
  │           with symmetric AES-256-GCM         │
```

The shared secret is never transmitted. An attacker who captures all packets sees only the public keys, and deriving the shared secret from public keys requires solving the Elliptic Curve Discrete Logarithm Problem -- computationally infeasible with current technology.

### Production TLS Issues

**Certificate expiration:** TLS certificates have expiration dates (typically 90 days for Let's Encrypt, 1 year for commercial CAs). If a certificate expires, every client receives a TLS error and refuses to connect. This is one of the most common causes of production outages, and it is entirely preventable with automated certificate rotation (e.g., cert-manager in Kubernetes).

**Certificate chain issues:** A server certificate is signed by an intermediate CA, which is signed by a root CA. The server must send the full chain (server cert + intermediate cert). If the intermediate is missing, some clients (like curl or Java's `HttpClient`) will reject the connection, while browsers may work because they cache intermediate certificates. This creates inconsistent failures that are maddening to debug.

```
Root CA (in client's trust store)
  │
  │ signs
  ▼
Intermediate CA (must be sent by server)
  │
  │ signs
  ▼
Server Certificate (sent by server, matches domain)
```

**TLS version and cipher mismatches:** If the server only supports TLS 1.3 but the client (e.g., an old Java 8 application) only supports TLS 1.2, the handshake fails. This is a common issue when upgrading infrastructure security while legacy clients still exist.

---

## 2.7 How Packets Travel Through a System

### The Full Journey of an HTTP Request

Let's trace a complete request from a user's browser to your Java service running in a Kubernetes cluster on AWS:

```
USER'S BROWSER (Sydney, Australia)
  │
  │  DNS: api.myapp.com → 54.200.1.100 (CloudFront edge IP)
  │
  ▼
AWS CLOUDFRONT (CDN Edge in Sydney)
  │
  │  Cache MISS (this is a POST request, not cacheable)
  │  Forward to origin
  │
  ▼
AWS INTERNET GATEWAY (us-east-1)
  │
  │  Packet enters the VPC
  │  Destination: internal ALB
  │
  ▼
AWS APPLICATION LOAD BALANCER (ALB)
  │  IP: 10.0.1.50 (private)
  │
  │  Terminates TLS (has the SSL certificate)
  │  Inspects HTTP headers
  │  Routes based on path: /api/* → target group "api-service"
  │
  │  Health check: /healthz returns 200?
  │  Selects a healthy target using round-robin
  │
  ▼
KUBERNETES NODE (EC2 instance: 10.0.2.30)
  │
  │  Packet arrives at the node's network interface (eth0)
  │
  ▼
IPTABLES / KUBE-PROXY
  │
  │  Kubernetes Service (ClusterIP: 10.96.45.67)
  │  kube-proxy has programmed iptables rules:
  │    10.96.45.67:8080 → DNAT to one of:
  │      10.244.1.15:8080 (pod on node-1)
  │      10.244.2.23:8080 (pod on node-2)
  │      10.244.3.8:8080  (pod on node-3)
  │
  │  Selected: 10.244.2.23:8080
  │
  ▼
VETH PAIR (virtual ethernet pair)
  │
  │  One end in the node's network namespace
  │  Other end in the pod's network namespace
  │  (This is how traffic enters the pod)
  │
  ▼
POD NETWORK NAMESPACE
  │
  │  The pod has its own IP: 10.244.2.23
  │  Its own network stack, routing table, iptables
  │
  ▼
YOUR JAVA APPLICATION (listening on 0.0.0.0:8080)
  │
  │  Tomcat/Netty accepts the connection
  │  Reads the HTTP request
  │  Processes the business logic
  │  Returns HTTP response
  │
  ▼
RESPONSE TRAVELS BACK (reverse path)
  Pod → veth → node → ALB → CloudFront → User's browser
```

### What Happens at Each Network Hop

At every hop, the packet's headers are inspected and potentially modified:

```
Original packet from the browser:
┌─────────────────────────────────────────────────┐
│ Src IP: 203.0.113.50 (user's public IP)         │
│ Dst IP: 54.200.1.100 (CloudFront)               │
│ Src Port: 52341                                  │
│ Dst Port: 443 (HTTPS)                            │
│ Payload: [encrypted HTTP request]                │
└─────────────────────────────────────────────────┘

After CloudFront → ALB (decrypted and re-encrypted):
┌─────────────────────────────────────────────────┐
│ Src IP: 10.0.0.50 (CloudFront internal)          │
│ Dst IP: 10.0.1.50 (ALB)                          │
│ Src Port: 38921                                   │
│ Dst Port: 443                                     │
│ X-Forwarded-For: 203.0.113.50 (original client)  │
│ Payload: [HTTP request]                           │
└─────────────────────────────────────────────────┘

After ALB → Kubernetes node:
┌─────────────────────────────────────────────────┐
│ Src IP: 10.0.1.50 (ALB)                          │
│ Dst IP: 10.0.2.30 (K8s node)                     │
│ Src Port: 44812                                   │
│ Dst Port: 30080 (NodePort)                        │
│ Payload: [HTTP request]                           │
└─────────────────────────────────────────────────┘

After kube-proxy DNAT → pod:
┌─────────────────────────────────────────────────┐
│ Src IP: 10.0.1.50 (ALB -- preserved)              │
│ Dst IP: 10.244.2.23 (pod IP -- DNATed)            │
│ Src Port: 44812                                   │
│ Dst Port: 8080 (container port)                   │
│ Payload: [HTTP request]                           │
└─────────────────────────────────────────────────┘
```

Notice how the destination IP changes at each hop (this is NAT -- Network Address Translation), but the original client IP is preserved in the `X-Forwarded-For` header. If your Java application needs to know the real client IP (for rate limiting, geo-routing, or logging), you must read `X-Forwarded-For`, not the source IP of the TCP connection.

---

## 2.8 NAT, Routing, Subnets, and VPC Concepts

### IP Addresses and CIDR Notation

Every device on a network has an IP address. IP addresses are organized into blocks using CIDR (Classless Inter-Domain Routing) notation:

```
10.0.0.0/16

│          │
│          └── The prefix length: the first 16 bits are the network part
│
└── The network address

10.0.0.0/16 in binary:

  00001010.00000000.00000000.00000000
  ├── network part ──┤├── host part ──┤
      (16 bits fixed)   (16 bits vary)

This block contains all IPs from:
  10.0.0.0 to 10.0.255.255
  = 65,536 addresses (2^16)
```

Common CIDR blocks and their sizes:

```
CIDR Block     │ Addresses │ Common Use
───────────────┼───────────┼──────────────────────────
/8             │ 16,777,216│ Large enterprise network
/16            │ 65,536    │ VPC (e.g., 10.0.0.0/16)
/20            │ 4,096     │ Large subnet
/24            │ 256       │ Typical subnet
/28            │ 16        │ Small subnet (e.g., ALB)
/32            │ 1         │ Single host
```

### Subnets

A subnet is a subdivision of a network. In AWS, subnets are tied to a specific Availability Zone and have either public or private internet access:

```
┌─────────────────────────── VPC: 10.0.0.0/16 ───────────────────────┐
│                                                                      │
│  Availability Zone: us-east-1a     Availability Zone: us-east-1b    │
│  ┌────────────────────────┐        ┌────────────────────────┐       │
│  │ PUBLIC SUBNET          │        │ PUBLIC SUBNET          │       │
│  │ 10.0.1.0/24            │        │ 10.0.2.0/24            │       │
│  │                        │        │                        │       │
│  │ ┌──────────────────┐   │        │ ┌──────────────────┐   │       │
│  │ │ ALB node         │   │        │ │ ALB node         │   │       │
│  │ │ NAT Gateway      │   │        │ │ NAT Gateway      │   │       │
│  │ └──────────────────┘   │        │ └──────────────────┘   │       │
│  │                        │        │                        │       │
│  │ Route table:           │        │ Route table:           │       │
│  │   10.0.0.0/16 → local  │        │   10.0.0.0/16 → local  │       │
│  │   0.0.0.0/0 → igw     │        │   0.0.0.0/0 → igw     │       │
│  └────────────────────────┘        └────────────────────────┘       │
│                                                                      │
│  ┌────────────────────────┐        ┌────────────────────────┐       │
│  │ PRIVATE SUBNET         │        │ PRIVATE SUBNET         │       │
│  │ 10.0.3.0/24            │        │ 10.0.4.0/24            │       │
│  │                        │        │                        │       │
│  │ ┌──────────────────┐   │        │ ┌──────────────────┐   │       │
│  │ │ K8s node-1       │   │        │ │ K8s node-2       │   │       │
│  │ │ 10.0.3.10        │   │        │ │ 10.0.4.10        │   │       │
│  │ │                  │   │        │ │                  │   │       │
│  │ │ K8s node-3       │   │        │ │ RDS Primary      │   │       │
│  │ │ 10.0.3.11        │   │        │ │ 10.0.4.50        │   │       │
│  │ └──────────────────┘   │        │ └──────────────────┘   │       │
│  │                        │        │                        │       │
│  │ Route table:           │        │ Route table:           │       │
│  │   10.0.0.0/16 → local  │        │   10.0.0.0/16 → local  │       │
│  │   0.0.0.0/0 → nat-gw  │        │   0.0.0.0/0 → nat-gw  │       │
│  └────────────────────────┘        └────────────────────────┘       │
│                                                                      │
│                    Internet Gateway (igw)                            │
│                         │                                            │
└─────────────────────────┼────────────────────────────────────────────┘
                          │
                       Internet
```

**Public subnet:** Has a route to the Internet Gateway (`0.0.0.0/0 → igw`). Resources in public subnets can have public IP addresses and be directly reachable from the internet.

**Private subnet:** Has a route to a NAT Gateway (`0.0.0.0/0 → nat-gw`). Resources in private subnets cannot be reached from the internet directly. They can initiate outbound connections (e.g., downloading packages, calling external APIs) through the NAT Gateway, which translates their private IP to the NAT Gateway's public IP.

**Why private subnets exist:** Defense in depth. Your application servers, databases, and internal services should not be directly reachable from the internet. Only load balancers and bastion hosts belong in public subnets.

### Network Address Translation (NAT)

NAT translates IP addresses as packets cross network boundaries. There are two common forms:

**Source NAT (SNAT) -- outbound from private subnet:**

```
Your Pod (10.244.2.23)
  │
  │  Wants to call: https://api.stripe.com (104.16.0.1)
  │
  │  Packet: Src=10.244.2.23 Dst=104.16.0.1
  │
  ▼
NAT Gateway (Public IP: 54.200.5.99)
  │
  │  Translates source IP:
  │  Src=10.244.2.23 → Src=54.200.5.99
  │
  │  Remembers the mapping:
  │  54.200.5.99:48321 ↔ 10.244.2.23:39012
  │
  │  Packet: Src=54.200.5.99:48321 Dst=104.16.0.1:443
  │
  ▼
Stripe API (104.16.0.1)
  │
  │  Responds to 54.200.5.99:48321
  │
  ▼
NAT Gateway
  │
  │  Reverse translates:
  │  Dst=54.200.5.99:48321 → Dst=10.244.2.23:39012
  │
  ▼
Your Pod receives the response
```

**Destination NAT (DNAT) -- inbound to services:**

This is what kube-proxy does. When traffic arrives for a Kubernetes Service IP (which is a virtual IP that does not exist on any interface), kube-proxy's iptables rules rewrite the destination to a real pod IP:

```
Incoming: Dst=10.96.45.67:8080 (Service ClusterIP)
                │
                │ iptables DNAT rule
                ▼
Rewritten: Dst=10.244.2.23:8080 (actual pod IP)
```

### Routing

Every machine has a routing table that determines where to send packets based on the destination IP:

```
$ ip route show
default via 10.0.3.1 dev eth0          ← Default route: unknown destinations go here
10.0.0.0/16 dev eth0 scope link        ← VPC traffic: send directly (same network)
10.244.0.0/16 dev cni0 scope link      ← Pod network: send via container network interface
172.17.0.0/16 dev docker0 scope link   ← Docker bridge: send via docker bridge
```

The kernel evaluates routes from most specific to least specific:
1. A packet for `10.244.2.23` matches `10.244.0.0/16` → send via `cni0`
2. A packet for `10.0.4.50` matches `10.0.0.0/16` → send via `eth0`
3. A packet for `104.16.0.1` matches no specific route → use default route via `10.0.3.1`

### Putting It All Together: A VPC Design for a Production System

Here is a complete network architecture for a production Java microservices system:

```
                         Internet
                            │
                            ▼
                   ┌─────────────────┐
                   │  Route 53 (DNS) │
                   │  api.myapp.com  │
                   │  → ALB IP       │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  WAF (Web       │
                   │  Application    │
                   │  Firewall)      │
                   │  Rate limiting, │
                   │  IP blocking,   │
                   │  SQL injection  │
                   │  protection     │
                   └────────┬────────┘
                            │
┌───────────────────────────┼──────────────────────────────────┐
│ VPC: 10.0.0.0/16          │                                   │
│                            ▼                                   │
│              ┌──────────────────────────┐                     │
│              │   Internet Gateway (igw) │                     │
│              └────────────┬─────────────┘                     │
│                           │                                    │
│    ┌──────────────────────┼───────────────────────┐           │
│    │ PUBLIC SUBNETS       │                        │           │
│    │                      ▼                        │           │
│    │        ┌──────────────────────┐               │           │
│    │        │  Application Load    │               │           │
│    │        │  Balancer (ALB)      │               │           │
│    │        │  Terminates TLS      │               │           │
│    │        │  Routes /api/* →     │               │           │
│    │        │  target group        │               │           │
│    │        └──────────┬───────────┘               │           │
│    │                   │                            │           │
│    │        ┌──────────┴───────────┐               │           │
│    │        │  NAT Gateway          │               │           │
│    │        │  (for outbound from   │               │           │
│    │        │   private subnets)    │               │           │
│    │        └──────────────────────┘               │           │
│    └───────────────────┬──────────────────────────┘           │
│                        │                                       │
│    ┌───────────────────┼──────────────────────────┐           │
│    │ PRIVATE SUBNETS   │                           │           │
│    │                   ▼                           │           │
│    │   ┌──────────────────────────────────────┐    │           │
│    │   │  EKS Cluster (Kubernetes)             │    │           │
│    │   │                                       │    │           │
│    │   │  ┌─────────┐ ┌─────────┐ ┌─────────┐ │    │           │
│    │   │  │ Node 1  │ │ Node 2  │ │ Node 3  │ │    │           │
│    │   │  │         │ │         │ │         │ │    │           │
│    │   │  │ Pod A   │ │ Pod A   │ │ Pod B   │ │    │           │
│    │   │  │ Pod B   │ │ Pod C   │ │ Pod C   │ │    │           │
│    │   │  └─────────┘ └─────────┘ └─────────┘ │    │           │
│    │   └──────────────────────────────────────┘    │           │
│    │                                                │           │
│    │   ┌──────────────────────────────────────┐    │           │
│    │   │  Data Layer                           │    │           │
│    │   │                                       │    │           │
│    │   │  ┌──────────┐  ┌──────────────────┐   │    │           │
│    │   │  │ RDS      │  │ ElastiCache      │   │    │           │
│    │   │  │ (Primary │  │ (Redis cluster)  │   │    │           │
│    │   │  │  +       │  │                  │   │    │           │
│    │   │  │ Replica) │  │                  │   │    │           │
│    │   │  └──────────┘  └──────────────────┘   │    │           │
│    │   └──────────────────────────────────────┘    │           │
│    └───────────────────────────────────────────────┘           │
│                                                                 │
│    SECURITY GROUPS (stateful firewalls per resource):           │
│      ALB SG:       Allow 443 from 0.0.0.0/0                   │
│      Node SG:      Allow 8080 from ALB SG only                │
│      RDS SG:       Allow 5432 from Node SG only               │
│      Redis SG:     Allow 6379 from Node SG only               │
│                                                                 │
│    NETWORK ACLs (stateless firewalls per subnet):              │
│      Public:       Allow 443 inbound, allow all outbound       │
│      Private:      Deny all inbound from internet              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Security Group Chains

Notice the security group design. It implements a chain of trust:

```
Internet ──▶ ALB (SG allows 443 from anywhere)
              │
              └──▶ K8s Nodes (SG allows 8080 ONLY from ALB's SG)
                    │
                    ├──▶ RDS (SG allows 5432 ONLY from Node SG)
                    │
                    └──▶ Redis (SG allows 6379 ONLY from Node SG)
```

If an attacker compromises the ALB, they can reach the K8s nodes on port 8080 but cannot reach the database on port 5432 directly. If an attacker gets access to a machine on the internet, they cannot reach the K8s nodes at all -- only the ALB is exposed. Each layer only permits the minimum necessary access from the layer above it.

This is the principle of **least privilege** applied to networking. It is why production systems use private subnets and why security groups are scoped to specific ports and source groups, not IP ranges.

---

## 2.9 Debugging Network Issues in Production

Understanding the theory is essential, but in production you need practical tools. Here are the commands and techniques that will save you during a 3 AM incident.

### Diagnosis Toolkit

**Is DNS working?**
```
$ dig api.payments.com +short
203.0.113.50

$ dig api.payments.com +trace    # Full recursive resolution trace

$ nslookup api.payments.com      # Simple lookup

# In a Kubernetes pod:
$ nslookup my-service.default.svc.cluster.local
```

**Can I reach the host?**
```
$ ping 203.0.113.50              # ICMP echo -- is the host alive?
                                  # Note: many cloud hosts block ICMP

$ traceroute 203.0.113.50        # Show every hop to the destination
                                  # Helps identify where packets are dropped

$ mtr 203.0.113.50               # Continuous traceroute -- shows packet loss per hop
```

**Is the port open?**
```
$ nc -zv 203.0.113.50 8080       # TCP connection test
Connection to 203.0.113.50 8080 port [tcp/*] succeeded!

$ curl -v https://api.payments.com/healthz
                                  # Full HTTP request with TLS handshake details

$ openssl s_client -connect api.payments.com:443
                                  # TLS certificate inspection
```

**What connections does my process have?**
```
$ ss -tnp                        # All TCP connections with process names
State     Recv-Q  Send-Q  Local Address:Port  Peer Address:Port  Process
ESTAB     0       0       10.0.3.10:8080      10.0.1.50:44812    java(12345)
ESTAB     0       0       10.0.3.10:45678     10.0.4.50:5432     java(12345)
CLOSE_WAIT 0      0       10.0.3.10:39012     10.0.4.60:6379     java(12345)

$ ss -s                           # Summary of all connection states
$ ss -tn state time-wait | wc -l  # Count TIME_WAIT connections
```

**What is happening on the wire?**
```
$ tcpdump -i eth0 port 8080 -nn   # Capture packets on port 8080
                                    # -nn: don't resolve hostnames/ports

$ tcpdump -i eth0 host 10.0.4.50 and port 5432 -w capture.pcap
                                    # Capture database traffic to a file
                                    # Open in Wireshark for analysis
```

### A Real Debugging Scenario

**Symptom:** Your Java service in Kubernetes cannot connect to an external API. The error is `java.net.ConnectException: Connection timed out`.

**Systematic diagnosis:**

```
Step 1: Is DNS resolving?
  $ kubectl exec -it my-pod -- nslookup api.external.com
  Server:    10.96.0.10
  Name:      api.external.com
  Address:   104.18.25.99
  ✓ DNS works

Step 2: Can I reach the IP?
  $ kubectl exec -it my-pod -- nc -zv -w 5 104.18.25.99 443
  nc: connect to 104.18.25.99 port 443 (tcp) timed out
  ✗ Cannot connect

Step 3: Is it a pod-level issue or a node-level issue?
  $ ssh node-1
  $ nc -zv -w 5 104.18.25.99 443
  Connection to 104.18.25.99 443 port [tcp/https] succeeded!
  ✓ Works from the node

Step 4: The problem is between the pod and the node.
  Possible causes:
    - Network policy blocking egress from the pod
    - Missing NAT rule for pod-to-external traffic
    - kube-proxy or CNI plugin issue

Step 5: Check network policies
  $ kubectl get networkpolicy -n my-namespace
  NAME              POD-SELECTOR      AGE
  restrict-egress   app=my-service    2d

  $ kubectl describe networkpolicy restrict-egress
  Egress:
    To:
      - namespaceSelector:
          matchLabels:
            kubernetes.io/metadata.name: my-namespace
    Ports:
      - 8080/TCP

  ★ Found it! The network policy only allows egress to pods
    within the same namespace on port 8080. External traffic
    is blocked.

Fix: Add an egress rule allowing traffic to 0.0.0.0/0 on port 443,
     or to the specific external IP range.
```

This systematic approach -- DNS, then connectivity, then narrow down the scope -- works for virtually every network issue.

---

## Chapter Summary

This chapter built the operating system and networking foundation that everything else in this book depends on:

1. **Processes are the fundamental unit of execution.** Understanding process lifecycle, states, and resource management (PIDs, file descriptors, memory) is essential for debugging container and application issues.

2. **System calls are the boundary between your code and the kernel.** Every file read, network connection, and memory allocation crosses this boundary. Tools like `strace` let you see exactly what your application is asking the kernel to do.

3. **The filesystem hierarchy is predictable.** `/proc` and `/sys` are virtual filesystems that expose live kernel state, and they are indispensable for production debugging.

4. **TCP is a stateful protocol with complex lifecycle.** Connection establishment (three-way handshake), data transfer, and teardown each have production implications -- SYN floods, TIME_WAIT exhaustion, CLOSE_WAIT leaks.

5. **DNS is a distributed, hierarchical, cached system.** JVM caching, Kubernetes search domains, and TTL settings are common sources of production failures.

6. **TLS protects data in transit using asymmetric key exchange and symmetric encryption.** Certificate management (expiration, chain completeness) is a frequent cause of outages.

7. **Packets traverse multiple network hops, each potentially modifying headers.** Understanding NAT, routing, and IP rewriting is essential for debugging connectivity in cloud environments.

8. **VPC architecture (subnets, security groups, NAT gateways, routing tables) implements defense in depth.** Private subnets, security group chaining, and least-privilege access control are the foundation of secure cloud networking.

In the next chapter, we will build on this foundation to understand containers: how Docker uses Linux namespaces and cgroups to create isolated environments, how images are layered, and how the container lifecycle works at the OS level.

---

*Previous: [Chapter 1 -- DevOps Philosophy & Staff Engineer Mindset](./01-devops-philosophy-and-staff-engineer-mindset.md)*

*Next: [Chapter 3 -- Docker & Container Internals](./03-docker-and-container-internals.md)*
