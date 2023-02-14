# netscaler-acl-parser

## Usage

```console
root@localhost: python3 ~/netscaler-acl-parser.py -h
usage: netscaler-acl-parser.py [-h] (-f ACL_FILE | -i) [-o OUTPUT_FILE] [-j] [-a ADDRESS] [-u USERNAME] [-p PASSWORD] [-w]

options:
  -h, --help            show this help message and exit
  -f ACL_FILE, --acl-file ACL_FILE
                        set acl file location
  -i, --interactive     retrive data from an active appliance
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        write output to file
  -j, --output-json     output in json format
  -a ADDRESS, --address ADDRESS
                        set custom ip address
  -u USERNAME, --username USERNAME
                        set custom username
  -p PASSWORD, --password PASSWORD
                        set custom password
  -w, --warnings        print warnings
```

## Examples

```console
root@localhost:~$ # example ACL file
root@localhost:~$ cat ~/tmp_acl.txt
Example ACL:
1)	Name: test_advanced_acl                        
   	Action: ALLOW                          Hits: 4
   	srcIP = 192.168.1.1
   	destIP = 10.1.1.1
   	srcMac:                                
   	Protocol: TCP 
   	srcPort                                destPort = 25
   	Vlan:                                 Interface:  
   	Active Status: ENABLED                 Applied Status: APPLIED
   	Priority: 10                           NAT: NO
   	TTL: 
   	Log Status: DISABLED                    
   	Forward Session: NO
   	Stateful: NO  
Example ACL:
12)	Name: test_advanced_acl                        
   	Action: ALLOW                          Hits: 150
   	srcIP = 192.168.1.15
   	destIP = 10.1.1.15
   	srcMac:                                
   	Protocol: TCP 
   	srcPort                                destPort = 443
   	Vlan:                                 Interface:  
   	Active Status: ENABLED                 Applied Status: APPLIED
   	Priority: 10                           NAT: NO
   	TTL: 
   	Log Status: DISABLED                    
   	Forward Session: NO
   	Stateful: NO  
 Done
root@localhost:~$
```

```console
root@localhost:~$ # get ACL from active appliance with interactive password prompt and output to file
root@localhost:~$ python3 ~/netscaler-acl-parser.py -i -a 192.168.1.10 -u nsroot -o ~/acl.csv
root@localhost:~$ cat ~/acl.csv
id,name,action,hits,source ip,destination ip,source mac,protocol,source port,destination port,vlan,interface,active status,applied status,priority,nat,ttl,log status,forward session,stateful
1,test_advanced_acl,ALLOW,4,192.168.1.1,10.1.1.1,,TCP,0,25,,Interface:,ENABLED,APPLIED,10,NO,,DISABLED,NO,NO
12,test_advanced_acl,ALLOW,150,192.168.1.15,10.1.1.15,,TCP,0,443,,Interface:,ENABLED,APPLIED,10,NO,,DISABLED,NO,NO
root@localhost:~$
```

```console
root@localhost:~$ # read ACL from file, print output to console
root@localhost:~$ python3 ~/netscaler-acl-parser.py -f ~/acl-raw.txt
id,name,action,hits,source ip,destination ip,source mac,protocol,source port,destination port,vlan,interface,active status,applied status,priority,nat,ttl,log status,forward session,stateful
1,test_advanced_acl,ALLOW,4,192.168.1.1,10.1.1.1,,TCP,0,25,,Interface:,ENABLED,APPLIED,10,NO,,DISABLED,NO,NO
12,test_advanced_acl,ALLOW,150,192.168.1.15,10.1.1.15,,TCP,0,443,,Interface:,ENABLED,APPLIED,10,NO,,DISABLED,NO,NO
root@localhost:~$
```

```console
root@localhost:~$ # read ACL from file, print warnings and output in json format to console
root@localhost:~$ python3 ~/netscaler-acl-parser.py -f ~/acl-raw.txt -w -j
WARNING: Parser not implemented for line:  Example ACL:
WARNING: Parser not implemented for line:  Example ACL:
{
    "action": "ALLOW",
    "dstIP": "10.1.1.1",
    "dstPort": 25,
    "forward_session": "NO",
    "hits": 4,
    "id": "1",
    "interface": "Interface:",
    "is_active": "ENABLED",
    "is_applied": "APPLIED",
    "log": "DISABLED",
    "name": "test_advanced_acl",
    "nat": "NO",
    "priority": 10,
    "protocol": "TCP",
    "srcIP": "192.168.1.1",
    "srcMac": "",
    "srcPort": 0,
    "stateful": "NO",
    "ttl": "",
    "vlan": ""
}{
    "action": "ALLOW",
    "dstIP": "10.1.1.15",
    "dstPort": 443,
    "forward_session": "NO",
    "hits": 150,
    "id": "12",
    "interface": "Interface:",
    "is_active": "ENABLED",
    "is_applied": "APPLIED",
    "log": "DISABLED",
    "name": "test_advanced_acl",
    "nat": "NO",
    "priority": 10,
    "protocol": "TCP",
    "srcIP": "192.168.1.15",
    "srcMac": "",
    "srcPort": 0,
    "stateful": "NO",
    "ttl": "",
    "vlan": ""
}
root@localhost:~$
```
