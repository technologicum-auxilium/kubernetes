import json
import subprocess
import sys


def get_vagrant_hosts():
    p = subprocess.Popen("vagrant ssh-config",
                         stdout=subprocess.PIPE,
                         shell=True)
    raw = p.communicate()[0]
    lines = raw.split("\n\n")
    vagrant_hosts = list()
    for line in lines:
        if line != '':
            sshconfig = dict()
            host_detail = line.strip().split("\n")
            for host_param in host_detail:
                kv = host_param.strip().split(' ')
                if len(kv) == 2:
                    sshconfig[kv[0]] = kv[1]
            vagrant_hosts.append(sshconfig)
    return vagrant_hosts


def to_ansible_inventory(hosts_with_vars):
    ansible_hosts = dict()
    master_hosts = list()
    worker_hosts = list()

    for host_entry in hosts_with_vars:
        host_name = host_entry['name']
        if 'master' in host_name:
            master_hosts.append(host_name)
        elif 'worker' in host_name:
            worker_hosts.append(host_name)

    ansible_hosts['master'] = {
        "hosts": master_hosts
    }
    ansible_hosts['worker'] = {
        "hosts": worker_hosts
    }

    ansible_hosts['_meta'] = {
        "hostvars": {
            host['name']: {
                "ansible_ssh_host": host.get('ansible_ssh_host', ''),
                "ansible_ssh_port": host.get('ansible_ssh_port', ''),
                "ansible_ssh_user": host.get('ansible_ssh_user', ''),
                "ansible_ssh_private_key_file": host.get('ansible_ssh_private_key_file', ''),
            }
            for host in hosts_with_vars
        }
    }

    return ansible_hosts


def main():
    # Adicionar as variáveis a todos os hosts
    vagrant_hosts = get_vagrant_hosts()
    hosts_with_vars = []
    for host_entry in vagrant_hosts:
        host_entry_with_vars = {
            'name': host_entry['Host'],
            'vars': {}
        }
        hosts_with_vars.append(host_entry_with_vars)

    output = to_ansible_inventory(hosts_with_vars)
    if sys.argv[1] == '--list':
        print(json.dumps(output))
    elif sys.argv[1] == '--host':
        print(json.dumps(output.get('_meta').get('hostvars').get(sys.argv[2])))
    else:
        print('Invalid argument.')


if __name__ == '__main__':
    main()
