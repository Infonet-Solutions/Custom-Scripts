#!/usr/bin/python3

###
# Title: NetScaler ACL to CSV
# Version: 0.1
# Last Update: 2023-02-13
# Description: Parse the output of the "show acl -format FORMATTED" command from the NetScaler CLI
#              and convert it into a CSV for further analysis. Can read data from a txt file or
#              directly from an active appliance
# Author: Emil Pandocchi
# Notes: ACLs can be collected with the following command:
#        > ssh -l nsroot <NetScaler IP> "show acl -format FORMATTED" >> /tmp/acl.txt
#        or by supplying NetScaler address, username and password
#
#        "-format FORMATTED" has been used to parse active data like ACL hits
#
# Example ACL:
# 1)	Name: test_advanced_acl                        
#   	Action: ALLOW                          Hits: 4
#   	srcIP = 192.168.1.1
#   	destIP = 10.1.1.1
#   	srcMac:                                
#   	Protocol: TCP 
#   	srcPort                                destPort = 25
#   	Vlan:                                 Interface:  
#   	Active Status: ENABLED                 Applied Status: APPLIED
#   	Priority: 10                           NAT: NO
#   	TTL: 
#   	Log Status: DISABLED                    
#   	Forward Session: NO
#   	Stateful: NO  
###

# imports
import argparse
import sys
import re
import subprocess
import json
import shutil

# create a parser for cli flags
parser = argparse.ArgumentParser()

# set arguments
group = parser.add_mutually_exclusive_group()
group.add_argument("-f", "--acl-file", help="set acl file location")
group.add_argument("-i", "--interactive", help="retrive data from an active appliance", action="store_true")
group.required = True

parser.add_argument("-o", "--output-file", help="write output to file")
parser.add_argument("-j", "--output-json", action="store_true", help="output in json format")
parser.add_argument("-a", "--address", help="set custom ip address", required='-i' in sys.argv)
parser.add_argument("-u", "--username", default="nsroot", help="set custom username")
parser.add_argument("-p", "--password", default="nsroot", help="set custom password")

parser.add_argument("-w", "--warnings", action="store_true", help="print warnings")

# parse arguments
args = parser.parse_args()

# set variables
acl_file_lines = list()
parsed_lines = list()

# check if we have an acl file to read
if args.acl_file:
    acl_file_lines = open(args.acl_file, "r").readlines()

# check if we need to write output to file
if args.output_file:
    parsed_file = open(args.output_file, "w")

# check if interactive
if args.interactive:
    # if we have a password, ensure we can use sshpass
    # otherwise we will fallback to plain ssh with interactive
    # password prompt

    # set command to fetch acl from appliance
    cmd = "show acl -format FORMATTED"

    # check if we have a password
    if args.password:
        # check if we can do a silent login with sshpass
        if shutil.which("sshpass"):
            ssh_cmd = [
                "sshpass",
                "-o StrictHostKeyChegking=no",
                "-p",
                args.password,
                args.username + "@" + args.address,
                cmd,
            ]

        else:
            print("Missing sshpass, fallback to plain ssh with interactive password prompt")

            # construct ssh command
            ssh_cmd = [
                "ssh",
                "-o StrictHostKeyChecking=no", # ignore new devices warnings
                args.username + "@" + args.address,
                cmd,
            ]

    # if we don't have a password just use plain ssh
    else:
        # construct ssh command
        ssh_cmd = [
            "ssh",
            "-o StrictHostKeyChecking=no", # ignore new devices warnings
            args.username + "@" + args.address,
            cmd,
        ]

    # structure subprocess command
    ssh = subprocess.Popen(
        ssh_cmd,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # read command output
    acl = ssh.stdout.readlines()

    # converts from bytes to strings
    for line in acl:
        acl_file_lines.append(line.decode("UTF-8"))

# object to store acl data
class Line:
    def ToJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    id: int
    name: str
    action: str
    hits: int
    srcIP: str
    dstIP: str
    srcMac: str
    protocol: str
    srcPort: int
    dstPort: int
    vlan: str
    interface: str
    is_active: str
    is_applied: str
    priority: int
    nat: str
    ttl: int
    log: str
    forward_session: str
    stateful: str

for line in acl_file_lines:
    # find starting lines
    if re.match("^\d+\)", line):
        # if it's a starting line we need a new object to populate
        l = Line()

        splitted = line.split(" ")

        l.id = splitted[0].split("\t")[0].strip(")")
        l.name = splitted[1].strip().strip("\n")

        parsed_lines.append(l)

    elif re.match("\s+Action", line):
        splitted = line.strip().split(" ")
        act = splitted[1]
        hits = splitted[-1]

        parsed_lines[-1].action = act
        parsed_lines[-1].hits = int(hits.strip("\n"))

    elif re.match("\s+srcIP", line):
        try:
            ip = line.strip().split("=")[1]
        except IndexError:
            ip = ""
        parsed_lines[-1].srcIP = ip.strip().strip("\n")

    elif re.match("\s+destIP", line):
        try:
            ip = line.strip().split("=")[1]
        except IndexError:
            ip = ""
        parsed_lines[-1].dstIP = ip.strip().strip("\n")

    elif re.match("\s+srcMac", line):
        try:
            parsed_lines[-1].srcMac = line.strip().strip("srcMac:")[1].strip().strip("\n")
        except IndexError:
            parsed_lines[-1].srcMac = ""
    
    elif re.match("\s+Protocol", line):
        proto = line.strip().split(":")[1].strip()
        parsed_lines[-1].protocol = proto

    elif re.match("\s+srcPort", line):
        splitted = line.strip().split(" ")

        parsed_lines[-1].srcPort = 0 # Todo: Fix source port parsing (can be missing)
        parsed_lines[-1].dstPort = int(splitted[-1].strip("\n"))

    elif re.match("\s+Vlan", line):
        splitted = line.strip().split(" ")
        
        parsed_lines[-1].vlan = splitted[1].strip().strip("\n")
        parsed_lines[-1].interface = splitted[-1].strip().strip("\n")

    elif re.match("\s+Active Status", line):
        splitted = line.strip().split(" ")

        parsed_lines[-1].is_active = splitted[2].strip().strip("\n")
        parsed_lines[-1].is_applied = splitted[-1].strip().strip("\n")

    elif re.match("\s+Priority", line):
        splitted = line.strip().split(" ")

        parsed_lines[-1].priority = int(splitted[1].strip().strip("\n"))
        parsed_lines[-1].nat = splitted[-1].strip().strip("\n")

    elif re.match("\s+TTL", line):
        parsed_lines[-1].ttl = line.strip().split("TTL:", 2)[1].strip().strip("\n")

    elif re.match("\s+Log Status", line):
        parsed_lines[-1].log = line.strip().split("Log Status:")[1].strip().strip("\n")

    elif re.match("\s+Forward Session", line):
        parsed_lines[-1].forward_session = line.strip().split("Forward Session:")[1].strip().strip("\n")

    elif re.match("\s+Stateful", line):
        parsed_lines[-1].stateful = line.strip().split("Stateful:")[1].strip().strip("\n")

    elif re.match("\s+Done", line) or re.match("Done", line):
        continue

    # generate a warning for every line we don't know how to parse.
    # this should not be a problem and will not be printed unless required
    # with the -w/--warnings flag
    else:
        if args.warnings:
            print("WARNING: Parser not implemented for line: ", line, end="")
            continue

# check if we actually parsed something
if len(parsed_lines) == 0:
    print("unable to find any suitable ACL to parse")
    exit(1)

# format header, csv is comma separated
header = (
            "id" +
            ",name" +
            ",action" +
            ",hits" +
            ",source ip" +
            ",destination ip" +
            ",source mac" +
            ",protocol" +
            ",source port"  +
            ",destination port" +
            ",vlan" +
            ",interface" +
            ",active status" +
            ",applied status" +
            ",priority" +
            ",nat" +
            ",ttl" +
            ",log status" +
            ",forward session" +
            ",stateful\n"
        )

# write header if we have to
if args.output_json:
    pass
elif args.output_file:
    parsed_file.write(header)
else:
    print(header, end="")

# iterate parsed lines
for line in parsed_lines:
    # Todo: poor fix for missing srcPort
    try:
        line.srcPort
    except AttributeError:
        line.srcPort = ""

    # Todo: poor fix for missing dstPort
    try:
        line.dstPort
    except AttributeError:
        line.dstPort = ""

    # print to json if required
    if args.output_json:
        l = line.ToJSON()
    # else construct line as csv
    else:
        l = (
            str(line.id) + "," +
            line.name + "," + 
            line.action + "," + 
            str(line.hits) + "," + 
            line.srcIP + "," + 
            line.dstIP + "," + 
            line.srcMac + "," + 
            line.protocol + "," + 
            str(line.srcPort)+ "," + 
            str(line.dstPort) + "," + 
            str(line.vlan) + "," + 
            line.interface + "," + 
            line.is_active + "," + 
            line.is_applied + "," + 
            str(line.priority) + "," + 
            line.nat + "," + 
            str(line.ttl) + "," + 
            line.log + "," + 
            line.forward_session + "," + 
            line.stateful + "\n"
        )    

    # write to file if we got one
    if args.output_file:
        parsed_file.write(l)
    # else print to stdout
    else:
        print(l, end="")

# close csv file if we got one
if args.output_file:
    parsed_file.close()
