import subprocess
import json

from ContainerNotFound import ContainerNotFound
from IPy import IP


class VZ:
    ctid = ""

    def validate(self, val):
        # check if the input is a ctid,ip or invalid

        try:
            ctid = int(val)
            if ctid >= 100:
                return "CTID"

        except ValueError:
            # not a ctid
            pass
        try:
            ip = IP(val)
            return "IP"
        except:
            # not an IP
            pass
        return None

    def get_all_json(self):
        # use ip to get the ctid of vm

        # get list of all vms and their ctid + ips in json format
        output = subprocess.check_output("/usr/sbin/vzlist -ao ctid,ip --json", shell=True)

        # getting rid of binary string
        output = output.decode('utf-8')

        vms = json.loads(output)

        return vms

    def check_ctid(self):
        vms = self.get_all_json()

        # loop through all the vms checking all their ips
        # if you find one that has the required ip, return its ctid
        for vm in vms:
            if str(vm['ctid']) == self.ctid:
                return True

        # if it cannot be found, return None
        return None

    def get_ctid(self, ip):

        vms = self.get_all_json()

        # loop through all the vms checking all their ips
        # if you find one that has the required ip, return its ctid
        for vm in vms:
            for address in vm['ip']:
                if address == ip:
                    return str(vm['ctid'])

        # if it cannot be found, return None
        return None

    def enable_ppp(self):
        # user vzctl to enable ppp

        # shutdown vm
        ret = subprocess.call("/usr/sbin/vzctl stop {}".format(self.ctid), shell=True)

        if ret == 0:
            # enable tun
            ret = subprocess.call("/usr/sbin/vzctl set {} --features ppp:on --save".format(self.ctid), shell=True)
        else:
            return False

        if ret == 0:
            # start vm again
            ret = subprocess.call("/usr/sbin/vzctl start {}".format(self.ctid), shell=True)
        else:
            return False

        if ret == 0:
            # enable devices
            subprocess.call("/usr/sbin/vzctl set {} --devices c:108:0:rw --save".format(self.ctid), shell=True)
        else:
            return False

        if ret == 0:
            # not checking return code, it is always 8
            subprocess.call("/usr/sbin/vzctl exec {} mknod /dev/ppp c 108 0".format(self.ctid), shell=True)
        else:
            # return False
            ret = subprocess.call("/usr/sbin/vzctl exec {}  chmod 600 /dev/ppp".format(self.ctid), shell=True)

        if ret == 0:
            return True
        else:
            return False

    def enable_tun(self):
        # use vzctl to enable tun

        # shutdown vm
        ret = subprocess.call("/usr/sbin/vzctl stop {}".format(self.ctid), shell=True)

        if ret == 0:
            # enable tun
            ret = subprocess.call("/usr/sbin/vzctl set {} --devnodes net/tun:rw --capability net_admin:on --save".format
                                  (self.ctid), shell=True)
        else:
            return False

        if ret == 0:
            # start vm again
            ret = subprocess.call("/usr/sbin/vzctl start {}".format(self.ctid), shell=True)
        else:
            return False

        if ret == 0:
            return True
        else:
            return False

    def __init__(self, vmid):
        # check if vm id is valid
        if self.validate(vmid) == "CTID":
            self.ctid = vmid
            if self.check_ctid() is None:
                raise ContainerNotFound
        elif self.validate(vmid) == "IP":
            self.ctid = self.get_ctid(vmid)
            if self.ctid is None:
                raise ContainerNotFound
        else:
            raise ValueError
