#!/usr/bin/env python3
# enables and disables tun for openvz containers

import sys
from vz import VZ
from ContainerNotFound import ContainerNotFound


def enable_tuns(vm_list):
    # figure out if is a list of ips or ctids
    # then loop through them to activate

    for vm in vm_list:
        container = None

        try:
            container = VZ(vm)
            if container.enable_tun():
                print("Tun enabled for CTID: " + container.ctid)
            else:
                print("Tun failed to enable for CTID: " + container.ctid)
        except ContainerNotFound:
            print("Container: " + vm + " does not exist")
        except ValueError:
            print("Invalid format: " + vm + " must be either an ip or ctid (192.168.1.1 : 101)")


def printhelp():
    # print syntax
    print("tun <ctid> ... | <ip> ...")


def main():

    if "--help" in sys.argv:
        printhelp()
    elif len(sys.argv) > 2:
        # more than one vm needs tun enabled
        enable_tuns(sys.argv[1:])
    elif len(sys.argv) == 2:
        # just a single vm needs tun enabled
        val = sys.argv[1]
        vm = None
        try:
            vm = VZ(val)
            if vm.enable_tun():
                print("Tun enabled for CTID: " + vm.ctid)
            else:
                print("Tun failed to enable for CTID: " + vm.ctid)
        except ValueError:
            print("Invalid input. must either be a CTID or IP (101 or 192.168.1.1)")
        except ContainerNotFound:
            print("Container Does not Exist")

    else:
        # print out the help
        printhelp()

main()
