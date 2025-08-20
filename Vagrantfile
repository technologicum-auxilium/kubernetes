# -*- mode: ruby -*-
# vi: set ft=ruby :
VAGRANTFILE_API_VERSION = "2"

num_workers = 3

BRIDGE_IFACE = "Realtek PCIe GbE Family Controller"

NET_BRIDGE_PREFIX = "192.168.100"
MASTER_BRIDGE_IP  = "#{NET_BRIDGE_PREFIX}.10"

UBUNTU_BOX = "ubuntu/jammy64"

servers = [
  {
    name:       "master",
    box:        UBUNTU_BOX,
    ip_bridge:  MASTER_BRIDGE_IP,
    playbook:   "ansible/k8s/master.yaml",
    group:      "/Clusters/Kubernetes/Master",
    memory:     2048,
    cpus:       2
  }
]

(1..num_workers).each do |i|
  servers << {
    name:       "worker#{i}",
    box:        UBUNTU_BOX,
    ip_bridge:  "#{NET_BRIDGE_PREFIX}.#{10 + i}",
    playbook:   "ansible/k8s/worker.yaml",
    group:      "/Clusters/Kubernetes/Worker",
    memory:     4096,
    cpus:       2
  }
end

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  servers.each do |server|
    config.vm.define server[:name] do |cfg|
      cfg.vm.box      = server[:box]
      cfg.vm.hostname = server[:name]

      cfg.vm.network "public_network",
        ip: server[:ip_bridge],
        bridge: BRIDGE_IFACE,
        use_dhcp: false,
        adapter: 2,
        virtualbox__cableconnected: true

      cfg.vm.synced_folder ".", "/vagrant", disabled: true

      cfg.ssh.insert_key = false
      cfg.ssh.private_key_path = ['~/.vagrant.d/insecure_private_key', '~/.ssh/id_rsa']

      cfg.vm.provision "file",
        source:      "~/.ssh/id_rsa.pub",
        destination: "~/.ssh/authorized_keys"

      cfg.vm.provision "shell", inline: <<-EOC
        set -e
        sudo sed -i -E 's/^#?PasswordAuthentication\\s+.*/PasswordAuthentication no/' /etc/ssh/sshd_config
        (sudo systemctl restart sshd.service || sudo service ssh restart) >/dev/null 2>&1 || true
        echo "finished"
      EOC

      cfg.vm.provider "virtualbox" do |vb|
        vb.name   = server[:name]
        vb.memory = server[:memory] || 4096
        vb.cpus   = server[:cpus]   || 2

        vb.customize ["modifyvm", :id, "--groups", server[:group]]
        vb.customize ["modifyvm", :id, "--uartmode1", "disconnected"]

        # NIC1 NAT
        vb.customize ["modifyvm", :id, "--nic1", "nat"]
        vb.customize ["modifyvm", :id, "--cableconnected1", "on"]

        # NIC2 Bridged
        vb.customize ["modifyvm", :id, "--cableconnected2", "on"]

        vb.customize ["modifyvm", :id, "--nic3", "none"]
        vb.customize ["modifyvm", :id, "--nic4", "none"]
      end

      cfg.vm.provision "ansible" do |ansible|
        ENV['ANSIBLE_CONFIG'] = "ansible.cfg"
        ansible.compatibility_mode = "2.0"
        ansible.playbook = server[:playbook]

        ansible.extra_vars = {
          master_ip: MASTER_BRIDGE_IP,
          node_ip: server[:ip_bridge],
          cidr: '10.244.0.0/16',
          user: 'vagrant'
        }
      end
    end
  end
end
