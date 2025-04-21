# GemiShell
Testing the Shell GPT's makeshift

## [+] 21-04-2025
--> Everything happens while python script is running. Drawback of this is, when a command goes wrong so we can only stop it from happening by CTRL+C which results in exit from python script too.

![image](https://github.com/user-attachments/assets/bd35b985-4d26-4307-a2b9-f1eff988eb5e)


I gave the prompt "identify my network and scan it with nmap" and it responded with 
```
---snip---
There\'s no single command to perfectly identify *your* network and then scan it with Nmap in all situations.The best approach depends on your network configuration (e.g., are you behind a router, what\'s your IP address?). However, here are a few options, progressing in complexity:\n\n**Option 1:  Simple (assumes you know your network\'s subnet)**\n\nIf you know your network\'s subnet (e.g., `192.168.1.0/24`)
---snip---
```

a very basic solution of my prompt would be "ipconfig" or else "ip add", so for instance we are using ip add

```bash
interface=$(ip -o -4 route show to default | awk '{print $5}')       # To get the interface which is handling traffic [eth0]
ip_info=$(ip -o -4 addr show dev $interface)                         # To get the ip info from that interface [eth0 details]
ip_address=$(echo $ip_info | awk '{print $4}')                       # Grab the IP [Gets the IP with CIDR from eth0 details]
nmap -sn $ip_address
```
