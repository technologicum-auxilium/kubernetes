# -*- mode: ruby -*-
# vi: set ft=ruby :
VAGRANTFILE_API_VERSION = "2"

require "fileutils"

num_masters = 3
num_workers = 3

BRIDGE_IFACE = "Realtek PCIe GbE Family Controller"
NET_BRIDGE_PREFIX = "192.168.100"
UBUNTU_BOX = "ubuntu/jammy64"

# IPs dos masters começam em .10
MASTER_BASE_IP = 10
# Workers começam depois dos masters
WORKER_BASE_IP = MASTER_BASE_IP + num_masters

servers = []

# Masters
(1..num_masters).each do |i|
  servers << {
    name:       "master#{i}",
    box:        UBUNTU_BOX,
    ip_bridge:  "#{NET_BRIDGE_PREFIX}.#{MASTER_BASE_IP + (i-1)}",
    playbook:   "ansible/k8s/master.yaml",
    group:      "/Clusters/Kubernetes/Masters",
    memory:     2048,  # mínimo para controle
    cpus:       2,
    tags: {
      "server"   => "k8s",
      "type"     => "master",
      "provider" => "virtualbox",
      "env"      => "prd",
      "os"       => "ubuntu",
      "version"  => "22.04"
    }
  }
end

# Workers
(1..num_workers).each do |i|
  servers << {
    name:       "worker#{i}",
    box:        UBUNTU_BOX,
    ip_bridge:  "#{NET_BRIDGE_PREFIX}.#{WORKER_BASE_IP + (i-1)}",
    playbook:   "ansible/k8s/worker.yaml",
    group:      "/Clusters/Kubernetes/Workers",
    memory:     4096,
    cpus:       2,
    tags: {
      "server"   => "k8s",
      "type"     => "worker",
      "provider" => "virtualbox",
      "env"      => "prd",
      "os"       => "ubuntu",
      "version"  => "22.04"
    }
  }
end

# --- Gera inventário Ansible comum ---
inventory_path = File.join(__dir__, "ansible", "k8s", "inventory", "vagrant.ini")
FileUtils.mkdir_p(File.dirname(inventory_path))

masters = []
workers = []
servers.each do |s|
  line = "#{s[:name]} ansible_host=#{s[:ip_bridge]} ansible_user=vagrant ansible_ssh_private_key_file=#{File.expand_path("~/.vagrant.d/insecure_private_key")}"
  if s[:tags]["type"] == "master"
    masters << line
  else
    workers << line
  end
end

File.open(inventory_path, "w") do |f|
  f.puts "[master]"
  masters.each { |l| f.puts l }
  f.puts
  f.puts "[worker]"
  workers.each { |l| f.puts l }
  f.puts
  f.puts "[kubernetes:children]"
  f.puts "master"
  f.puts "worker"
end

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # --- Sem vbguest (se existir no host, desativa) ---
  if Vagrant.has_plugin?("vagrant-vbguest")
    config.vbguest.auto_update = false
    config.vbguest.no_remote   = true
    config.vbguest.installer_options = { allow_kernel_upgrade: false }
  end

  servers.each do |server|
    config.vm.define server[:name] do |cfg|
      cfg.vm.box      = server[:box]
      cfg.vm.hostname = server[:name]

      # NIC2 (bridge) com IP fixo; NIC1 fica NAT
      cfg.vm.network "public_network",
        ip: server[:ip_bridge],
        bridge: BRIDGE_IFACE,
        use_dhcp: false,
        adapter: 2,
        virtualbox__cableconnected: true

      # Pasta sincronizada via rsync (dispensa Guest Additions)
      cfg.vm.synced_folder ".", "/vagrant",
        type: "rsync",
        rsync__args: ["--verbose", "--archive", "--delete", "-z"],
        rsync__exclude: [".git/", ".idea/", ".vscode/", "artifacts/"]

      # SSH
      cfg.ssh.insert_key = false
      cfg.ssh.private_key_path = ['~/.vagrant.d/insecure_private_key', '~/.ssh/id_rsa']
      cfg.ssh.keep_alive = true
      cfg.vm.boot_timeout = 600

      # Copia chave pública
      cfg.vm.provision "file",
        source:      "~/.ssh/id_rsa.pub",
        destination: "~/.ssh/authorized_keys"

      cfg.vm.provision "shell", inline: <<-EOC
        set -e
        sudo sed -i -E 's/^#?PasswordAuthentication\\s+.*/PasswordAuthentication no/' /etc/ssh/sshd_config
        (sudo systemctl restart sshd.service || sudo service ssh restart) >/dev/null 2>&1 || true
      EOC

      # VirtualBox provider
      cfg.vm.provider "virtualbox" do |vb|
        vb.name   = server[:name]
        vb.memory = server[:memory]
        vb.cpus   = server[:cpus]

        vb.customize ["modifyvm", :id, "--groups", server[:group]]
        vb.customize ["modifyvm", :id, "--uartmode1", "disconnected"]

        # NIC1 NAT
        vb.customize ["modifyvm", :id, "--nic1", "nat"]
        vb.customize ["modifyvm", :id, "--cableconnected1", "on"]

        # NIC2 Bridge (definida acima)
        vb.customize ["modifyvm", :id, "--cableconnected2", "on"]

        # Desliga NIC3/4
        vb.customize ["modifyvm", :id, "--nic3", "none"]
        vb.customize ["modifyvm", :id, "--nic4", "none"]

        # Tags (extradata)
        server[:tags].each do |k, v|
          vb.customize ["setextradata", :id, "custom:#{k}", v]
        end
      end

      # Provisionamento Ansible
      cfg.vm.provision "ansible" do |ansible|
        ENV['ANSIBLE_CONFIG'] = "ansible.cfg"
        ansible.compatibility_mode = "2.0"
        ansible.playbook = server[:playbook]

        # Inventário COMUM (tem [master] e [worker])
        ansible.inventory_path = inventory_path

        # Limitar a execução a esta VM (evita tentar conectar nas outras)
        ansible.limit = server[:name]

        ansible.extra_vars = {
          master_ip: "#{NET_BRIDGE_PREFIX}.#{MASTER_BASE_IP}",
          node_ip: server[:ip_bridge],
          cidr: '10.244.0.0/16',
          user: 'vagrant',
          ansible_connection: 'ssh',
          ansible_port: 22,
          ansible_user: 'vagrant',
          ansible_ssh_private_key_file: File.expand_path('~/.vagrant.d/insecure_private_key'),
          ansible_shell_type: 'sh',
          ansible_shell_executable: '/bin/bash',
          ansible_python_interpreter: '/usr/bin/python3'
        }

        # QoL
        ansible.host_key_checking = false
        ansible.raw_ssh_args = ["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null"]
      end
    end
  end
end
