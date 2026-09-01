# Step 3 — Exposure Observation

## HTTP server binding

When I started the Python HTTP server , the server was listening on:

```text
0.0.0.0:8000
[::]:8000
```

On Windows, `0.0.0.0` means that the server accepts all IPv4 network interfaces. `[::]` represents all IPv6 interfaces. So, the server was not restricted to the local computer and could be reached by other devices that could connect to the laptop over the network.

Then, I stopped the server and restarted it with:

```text
python -m http.server 8000 --bind 127.0.0.1
```

This time, `netstat` showed:

```text
127.0.0.1:8000
```

`127.0.0.1` is the loopback address. A service connected to this address accepts connections only from the same computer. Other devices on the network cannot connect to it through the laptop's network interfaces as before.

## Other listening services

After stopping my own HTTP server, I checked the other listening TCP ports on the laptop with:

```text
netstat -ano | findstr LISTENING
```

The results were interesting:

| Address and port  |   PID | Process      | Observation                                     |
| ----------------- | ----: | ------------ | ----------------------------------------------- |
| `0.0.0.0:3306`    | 13308 | `mysqld.exe` | MySQL was listening on all IPv4 interfaces.     |
| `[::]:3306`       | 13308 | `mysqld.exe` | MySQL was also listening on IPv6 interfaces.    |
| `0.0.0.0:16992`   | 12136 | `LMS.exe`    | Intel LMS was listening on all IPv4 interfaces. |
| `0.0.0.0:623`     | 12136 | `LMS.exe`    | The same process was listening on port 623.     |
| `127.0.0.1:11434` | 16820 | `ollama.exe` | Ollama was restricted to the local machine.     |

I confirmed the processes using `tasklist` and checked the ownership of ports 3306 and 16992 using `Get-NetTCPConnection`.

The most important observation is that not every listening service is necessarily a vulnerability, a service bound to `0.0.0.0` could be vulnerable but also depends on factors such as firewall or configuration.