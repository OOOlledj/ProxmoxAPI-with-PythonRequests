import json
import requests
import datetime
from urllib.parse import urlencode


class ProxmoxARM:
    def __init__(self, host: str, port: int, api_format: str, auth: dict, ):
        """
        Init request session for proxmox API
        ex.: (host='192.168.0.11', port=8006, api_format=
        """
        self.s = requests.Session()
        self.s.verify = False
        self.URL = f'https://{host}:{port}{api_format}'
        if auth.get('password'):
            self.set_ticket_cookie(auth)
        elif auth.get('token'):
            self.set_api_token(auth)
        else:
            print('Not known auth method')

    def set_ticket_cookie(self, auth: dict):
        """
        set access ticket with <username>@<realm> and <password>
        auth = {'username': <username>, 'realm': <realm>, 'password': <password>}
    ex. auth = {'username': 'root', 'realm': 'pam', 'password': 'some_password'}
        """
        ticket_text = self.s.post(url=f'{self.URL}/access/ticket', data=urlencode(auth))
        ticket = json.loads(ticket_text.text)['data']['ticket']
        self.s.cookies.set('PVEAuthCookie', ticket)

    def set_api_token(self, auth: dict):
        """
        set access token as Authorization header
        user = <name>@<realm>!<token_name>, ex. root@pam!test
        token = '********-****-****-****-************'
        """
        pve = f'{auth["username"]}@{auth["realm"]}!{auth["token_name"]}={auth["token"]}'
        self.s.headers.update({'Authorization': f'PVEAPIToken={pve}'})

    def GET(self, resource: str) -> requests.Response.text:
        """
        GET method for resource
        resource ex.: '/version', '/cluster/log'
        """
        r = self.s.get(url=f'{self.URL}{resource}')
        return r

    def POST(self, resource: str, data: str = '') -> requests.Response:
        """
        POST method for resource
        resource ex.: '/nodes/{node}/qemu/{vmid}/status/shutdown'
        """
        r = self.s.post(url=f'{self.URL}{resource}', data=data)
        return r

    def get_version(self):
        func = self.get_version
        r = self.GET('/version')
        version_info = json.loads(r.text)
        if self.check_success(version_info, func):
            return self.print_version(version_info)
        else:
            return 0

    @staticmethod
    def print_version(version: dict) -> list:
        data = version['data']
        r = data['release']
        v = data['version']
        print(f'Proxmox VE API {r} v{v}\n')
        return v

    def get_nodes(self):
        func = self.get_nodes
        r = self.GET('/nodes')
        nodes_info = json.loads(r.text)
        if self.check_success(nodes_info, func):
            return self.print_nodes(nodes_info)
        else:
            return 0

    def print_nodes(self, nodes: dict) -> list:
        names = []
        for node in nodes['data']:
            n = node['node']
            names.append(n)
            u = str(datetime.timedelta(seconds=node['uptime']))
            s = node['status']
            print(f'Node "{n}" - {s}, {u}')
            self.get_node_vms(n)
        return names

    def get_node_vms(self, node_name: str):
        func = self.get_node_vms
        r = self.GET(f'/nodes/{node_name}/qemu')
        node_qemu_info = json.loads(r.text)
        if self.check_success(node_qemu_info, func):
            self.print_node_vms(node_qemu_info)

    @staticmethod
    def print_node_vms(node_qemu_info: dict) -> None:
        for node in node_qemu_info['data']:
            n = node['name']
            s = node['status']
            vmid = node['vmid']
            print(f'   VM "{n}" - {vmid}, {s}')

    def start_node_vm(self, node_name: str, qemu_vmid: int):
        # func = self.start_node_vm
        r = self.POST(f'/nodes/{node_name}/qemu/{qemu_vmid}/status/start')
        print(f'Starting VM {qemu_vmid} result: {r.status_code}')

    def reboot_node_qemu(self, node_name: str, qemu_vmid: int):
        # func = self.reboot_node_vm
        r = self.POST(f'/nodes/{node_name}/qemu/{qemu_vmid}/status/reboot')
        print(f'Rebooting VM {qemu_vmid} result: {r.status_code}')

    def shutdown_node_qemu(self, node_name: str, qemu_vmid: int):
        # func = self.shutdown_node_qemu
        r = self.POST(f'/nodes/{node_name}/qemu/{qemu_vmid}/status/shutdown')
        print(f'Shutdown VM {qemu_vmid} result: {r.status_code}')

    def check_success(self, version_info: dict, func):
        if version_info['success']:
            return 1
        else:
            s = version_info['status']
            m = version_info['message']
            self.print_error(status_code=s, message=m, func=func)
            return 0

    @staticmethod
    def print_error(status_code, message, func):
        print(f'No success on {func.__name__}: {status_code}, {message}')
