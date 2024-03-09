# -*- mode: ruby -*-
# vi: set ft=ruby :
VAGRANTFILE_API_VERSION = "2"

num_workers = 2

servers = [
  {
    name: "master",
    box: "ubuntu/jammy64",
    ip_private: "192.168.56.10",
    playbook: "ansible/k8s/master.yaml",
    group: "/Kubernetes/Master"
  }
]

(1..num_workers).each do |i|
  servers << {
    name: "worker#{i}",
    box: "ubuntu/jammy64",
    ip_private: "192.168.56.#{i + 10}",
    playbook: "ansible/k8s/worker.yaml",
    group: "/Kubernetes/Worker"
  }
end

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  servers.each do |server|
    config.vm.define server[:name] do |config|
      config.vm.box = server[:box]
      config.vm.hostname = server[:name]  
      config.vm.network "private_network", ip: server[:ip_private]
      config.vm.synced_folder ".", "/vagrant", disabled: true
      config.ssh.insert_key = false
      config.ssh.private_key_path = ['~/.vagrant.d/insecure_private_key', '~/.ssh/id_rsa']
      config.vm.provision "file", source: "~/.ssh/id_rsa.pub", destination: "~/.ssh/authorized_keys"
      config.vm.provision "shell", inline: <<-EOC
      sudo sed -i -e "\\#PasswordAuthentication yes# s#PasswordAuthentication yes#PasswordAuthentication no#g" /etc/ssh/sshd_config
        sudo systemctl restart sshd.service
        echo "finished"
      EOC

      config.vm.provider "virtualbox" do |vb|
        vb.customize [ "modifyvm", :id, "--uartmode1", "disconnected" ]
        vb.name = server[:name]
        vb.memory = "2048" 
        vb.cpus = 2
        vb.customize ["modifyvm", :id, "--groups", server[:group]]
      end

      config.vm.provision "ansible" do |ansible|
        ENV['ANSIBLE_CONFIG'] = "ansible.cfg"
        ansible.compatibility_mode = "2.0"
        ansible.playbook = server[:playbook]
        ansible.extra_vars = {
          master_ip: "192.168.56.10",
          cidr: '10.244.0.0/16',
          node_ip: [:ip_private]
        }
      end
    end
  end
end
