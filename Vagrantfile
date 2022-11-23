# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "generic/fedora28"
  config.vm.hostname = "arteria-bclconvert-dev"

  config.vm.provider "virtualbox" do |vb|
    # Customize the amount of memory on the VM:
    vb.memory = "4000"
  end

  config.vm.provision "file", source: "./", destination: "/home/vagrant"

  config.vm.provision "shell", inline: <<-SHELL
    sudo yum update
    sudo yum install -y unzip python3-pip python3-virtualenv git gcc-c++

    sudo yum install -y local_files/bcl-convert-4.0.3-2.el7.x86_64.rpm
  SHELL
end
