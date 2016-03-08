#!/usr/bin/env python

#enables and disables tun for openvz containers

import sys,getopt,IPy,subprocess,json

from IPy import IP

def enabletun(ctid):
    #use vzctl to enable tun

    #shutdown vm
    subprocess.call("/usr/sbin/vzctl stop " + ctid,shell=True)
    #enable tun
    subprocess.call("/usr/sbin/vzctl set " + ctid + " --devnodes net/tun:rw --capability net_admin:on --save",shell=True)

    #start vm again
    subprocess.call("/usr/sbin/vzctl start " + ctid,shell=True)

    print("enabled tun for:",ctid)

def getctid(ip):
    #use ip to get the ctid of vm

    #get list of all vms and their ctid + ips in json format
    output = subprocess.check_output("/usr/sbin/vzlist -ao ctid,ip --json",shell=True)

    #getting rid of binary string
    output = output.decode('utf-8')

    vms = json.loads(output)

    #loop through all the vms checking all their ips
    #if you find one that has the required ip, return its ctid
    for vm in vms:
        for address in vm['ip']:
            if address ==ip:
                return str(vm['ctid'])

    #if it cannot be found, return None
    return None

def enabletuns(vms):
    #figure out if is a list of ips or ctids
    #then loop through them to activate

    for vm in vms:

        if validate(vm) == "CTID":
            enabletun(vm)
        elif validate(vm)== "IP":
            ctid = getctid(vm)
            enabletun(ctid)
        else:
            print("Invalid input. must either be a CTID or IP (101 or 192.168.1.1:",vm)

    print("enabling tun for multiple vms")

def validate(input):
    #check if the input is a ctid,ip or invalid

    valid = False
    try:
        ctid = int(input)
        return "CTID"
    except ValueError:
        #not a ctid
        pass
    try:
        ip = IP(input)
        return "IP"
    except:
        #not an IP
        pass

    return None

def printhelp():
    #print syntax
    print("tun <ctid> ... | <ip> ...")


def main():

    if "--help" in sys.argv:
        printhelp()
    elif len(sys.argv) > 2:
        #more than one vm needs tun enabled
        print("More than one vm needs tun enabled")
        enabletuns(sys.argv[1:])
    elif len(sys.argv) ==2:
        #just a single vm needs tun enabled
        input = sys.argv[1]
        if validate(input) == "CTID":
            enabletun(input)
        elif validate(input)== "IP":
            ctid = getctid(input)
            enabletun(ctid)
        else:
            print("Invalid input. must either be a CTID or IP (101 or 192.168.1.1")
    else:
        #print out the help
        printhelp()

main()