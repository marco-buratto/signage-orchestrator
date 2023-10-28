**SIGNAGE ORCHESTRATOR** 

Signage Orchestrator is a central web interface you can use to schedule Raspberry Slideshow and Raspberry Digital Signage units (“players”) to slide media/display web urls in a calendar-based timetable.

All available players are enlisted in the Players table (in the image only Slideshow players are available), if configured to use the Orchestrator.

You can add each player to a Group.

![Usage1](docs/usage/players.png)
![Usage2](docs/usage/groups.png)

Playlists are player configurations. 

Essentially, for Raspberry Slideshow a playlist is the <em>media.conf</em> directives, plus the transition and blend time of images:

![Usage3](docs/usage/slideshow.playlists.png)

For Raspberry Digital Signage, a playlist contains the following information:

![Usage4](docs/usage/web.playlists.png)

In the Events tab you can schedule a group of players to use a playlist (of course, Raspberry Slideshow players can only run Slideshow Playlists, while Raspberry Digital Signage players are only able to run Web Signage Playlists):

![Usage5](docs/usage/events.png)
![Usage6](docs/usage/events.detail.png)

Please note that in the Events tab you need to select the Group, then all events related to it will be displayed.

When adding a new event, just give it a name, then click on it, use the modification icon and assign it a playlist (as in the last image here above). 

In the images, for example, all the players associated to the "Mall public players group" will be scheduled, according to the calendar, to slide their associated playlist, which can be of course different from event to event.

------------

***Installation***

A Debian 12 Bookworm operating system is needed in order to deploy Signage Orchestrator.
System must be reachable by Raspberry Slideshow/Digital Signage players, so in the same network or correctly routed.

For testing purposes, a VirtualBox virtual machine with bridged network is fine.

Once installed the operating system, SSH in as root, then give the following commands:

    apt update

    cd /root
    wget https://github.com/marco-buratto/signage-orchestrator/releases/download/v1.1/signage-orchestrator-backend_1.1-1_all.deb
    wget https://github.com/marco-buratto/signage-orchestrator/releases/download/v1.1/signage-orchestrator-ui_1.1-1_all.deb

    apt install -y /root/signage-orchestrator-*.deb

During the installation, debconf will ask you to set the timezone according to yours and to create a password for the admin user of Signage Orchestrator, in order to be able to login and connect players. The following images are shown as an example:

![Installation1](docs/installation/install.1.png)
![Installation2](docs/installation/install.2.png)
![Installation3](docs/installation/install.3.png)

Please be sure the time of the operating system is always correct: configure systemd-timesyncd or install another NTP service for the purpose.

Just a note, the following APT message you'll see at the end of the process is NOT an error:

    N: Download is performed unsandboxed as root as file '/root/signage-orchestrator-backend_1.1-1_all.deb' couldn't be accessed by user '_apt'. - pkgAcquire::Run (13: Permission denied)


------------

***First access***

From your browser of choice, browse to the IP address of the host/vm you have just installed and agree to the security warnings. 
The default installation is deployed with an auto-signed certificate.

Login with *admin* as user and the password you have chosen.

By the way, Signage Orchestrator is designed with security in mind, but of course in production environments or "untrusted networks", a valid TLS certificate is needed to be installed into Apache.

------------

***Players connection***

All configured players (Pis running Raspberry Slideshow or Raspberry Digital Signage) are enlisted in the Players table if configured.
In order to configure a player, SSH into it as root, then:

    cd /tmp
    wget --no-check-certificate https://ORCHESTRATOR_ADDRESS/raspberry-player/player-connector.sh
    # or wget https://ORCHESTRATOR_ADDRESS/raspberry-player/player-connector.sh with a valid certificate on the Orchestrator.

    bash player-connector.sh --action install --player-type web|slideshow --orchestrator-address ORCHESTRATOR_ADDRESS --orchestrator-password ORCHESTRATOR_PASSWORD --player-name PLAYER_NAME --player-position PLAYER_OPTIONAL_POSITION_NOTES --player-comment PLAYER_OPTIONAL_COMMENT --check-tls yes|no

--player-type: on Raspberry Slideshow players use "slideshow"; on Raspberry Digital Signage players use "web".

ORCHESTRATOR_ADDRESS is the IP address or fqdn of your Signage Orchestrator installation and ORCHESTRATOR_PASSWORD is the password chosen when installing.

PLAYER_NAME, PLAYER_OPTIONAL_POSITION_NOTES, PLAYER_OPTIONAL_COMMENT are properties of the player (Raspberry unit) itself, so how it will be displayed in the Orchestrator interface.

--check-tls: use "no" unless you have installed a valid certificate on the Orchestrator.

