**DEVELOPMENT INFRASTRUCTURE**

Signage Orchestrator is composed by two services, a Python3 backend and a Vue.js frontend. 
In development, two Vagrant virtual machines are used, one for each node, backend and ui.

------------

**LINUX development host requirements**
- Tested on modern Debian and Ubuntu operating systems; any other should work.
- Vagrant and VirtualBox are needed.
- Vagrant:

      # Using Vagrant repos. 
      wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/vagrant-archive-keyring.gpg
      sudo echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
      sudo apt update
      sudo apt install vagrant
      sudo apt install nfs-kernel-server

- Vagrant plugins (user-installed: do not use _sudo_):
     
      vagrant plugin install vagrant-reload
      vagrant plugin install vagrant-env
      vagrant plugin install vagrant-fsnotify
      vagrant plugin install vagrant-disksize
      

- VirtualBox:
        
      # Ubuntu 20 for example.
      sudo apt install -y virtualbox virtualbox-dkms virtualbox-guest-additions-iso virtualbox-guest-dkms virtualbox-guest-utils virtualbox-guest-x11

- From VirtualBox 6.1.28 editing the file /etc/vbox/networks.conf is needed:
     
      [ ! -d /etc/vbox ] && mkdir /etc/vbox
      sudo echo '* 10.0.0.0/8' > /etc/vbox/networks.conf

- Codebases and Vagrant virtual machines:

      cd /path/to/signage-orchestrator/dev-setup
      vagrant up backend ui
      
    Guests will mount the host-side NFS share, where the codebase is saved.
	
    On the first run, Vagrant is going to create all the virtual machines, taking a good amount of time time. Keep relaxed.

    In order to avoid inserting the sudo password every time, use the following sudoers file. Make sue sudo is installed.
    
      sudo cat > /etc/sudoers.d/vagrant<<EOF
      # Host alias specification

      # User alias specification
      User_Alias VAGRANTERS = YOUR_USERNAME # replace YOUR_USERNAME

      # Cmnd alias specification
      Cmnd_Alias VAGRANTSH = /usr/bin/chown 0\:0 /tmp/*, /usr/bin/mv -f /tmp/* /etc/exports, /usr/bin/systemctl start nfs-server.service, /usr/bin/systemctl stop nfs-server.service, /usr/bin/systemctl start libvirtd.service, /usr/bin/systemctl stop libvirtd.service, /usr/sbin/exportfs -ar, /usr/sbin/sysctl -w fs.inotify.max_user_watches=*

      VAGRANTERS ALL=(root) NOPASSWD: VAGRANTSH
      EOF

------------

**LET'S GO!**

Once nodes are created and running:

 1. Browse to http://10.0.120.10:5173 to load the web GUI.
            
 2. Signage Orchestrator is an "API-first" project. A Postman collection in saved in backend/backend/docs. Install Postman first, and import it.

Operate into nodes:

        vagrant ssh <backend|ui>
        sudo -i

Each vm logs into syslog.

****BACKEND****

Use Postman to write/test APIs. This is usually the first place to start when coding: first master the backend logic its codebase, then the UI and the architecture.

A database GUI (phpMyAdmin) is available at http://10.0.120.100:8000/ 

Update database when schema changes: 

    # From the dev-setup folder.
    vagrant provision backend --provision-with db

****UI****

Restart the npm dev server after a modification, when it does not detect it automatically (ssh in the virtual machine as root, of course):

    systemctl restart npm 

****A FIRST TEST****

You can bring up player1Test and player2Test Vagrant nodes in order to have a first test of the platform without connecting real Raspberry Pi players:

    # From the dev-setup folder.
    vagrant up player1Test player2Test

Then connect each playerTest to the backend as a player:

    # From the dev-setup folder.
    vagrant ssh player1Test

    sudo -i
    wget http://10.0.120.10:5173/raspberry-player/player-connector.sh
    bash player-connector.sh --action install --player-type slideshow --orchestrator-address 10.0.120.100 --orchestrator-password "none" --player-name slideshow.one -check-tls no
    sed -i 's|https://|http://|g' /usr/bin/player.sh; sed -i 's|/backend/api/v1/backend/|/api/v1/backend/|g' /usr/bin/player.sh

    # Do the same for player2Test (changing player-name).

You will now see that the two players populate the backend database and are shown in the Players tab of the UI.

****BUILD****

In order to create the installation .deb packages, a quick make-release script is provided within each vm.

    # From the dev-setup folder.
    vagrant ssh backend
    sudo -i
    cd /var/www/backend
    bash DEBIAN-PKG/make-release.sh  --action deb

Package file will be available in the /tmp directory, you can scp it to your development host or move it into the /vagrant folder; in this case the file will be available in the dev-setup folder.

    # From the dev-setup folder.
    vagrant ssh ui
    sudo -i
    cd /var/www/ui
    bash DEBIAN-PKG/make-release.sh  --action deb

Package file will be available in the /tmp directory.
