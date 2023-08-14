import urllib3
from proxmox import ProxmoxARM
from config import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if __name__ == "__main__":

#   b = ProxmoxARM(host, port, api_format, auth_token) # with token
    b = ProxmoxARM(host, port, api_format, auth_ticket) # with password

    version = b.get_version()
    nodes = b.get_nodes()

    node_name = 'tortilla' # example name of node

#   start_node_100 = b.start_node_qemu(node_name, 100)
#   start_node_101 = b.start_node_qemu(node_name, 101)

#   reboot_node_100 = b.reboot_node_qemu(node_name, 100)

#   shutdown_101 = b.shutdown_node_qemu(node_name, 101)
#   shutdown_100 = b.shutdown_node_qemu(node_name, 100)

    # b.get_node_qemu(node_name='tortilla')
