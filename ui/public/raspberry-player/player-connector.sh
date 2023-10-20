#!/bin/bash

set -e

function System()
{
    base=$FUNCNAME
    this=$1

    # Declare methods.
    for method in $(compgen -A function)
    do
        export ${method/#$base\_/$this\_}="${method} ${this}"
    done

    # Properties list.
    ACTION="$ACTION"
    ORCHESTRATOR_ADDRESS="$ORCHESTRATOR_ADDRESS"
    ORCHESTRATOR_PASSWORD="$ORCHESTRATOR_PASSWORD"
    PLAYER_NAME="$PLAYER_NAME"
    PLAYER_POSITION="$PLAYER_POSITION"
    PLAYER_COMMENT="$PLAYER_COMMENT"
}

# ##################################################################################################################################################
# Public
# ##################################################################################################################################################

#
# Void System_run().
#
function System_run()
{
    if [ "$ACTION" == "install" ]; then
        System_requisitesInstall
        System_regeneratePublicKey
        System_setup
        System_playerServiceInstall
    fi
}

# ##################################################################################################################################################
# Private static
# ##################################################################################################################################################

function System_requisitesInstall()
{
    apt update
    apt install -y openssh-client jq
}


function System_regeneratePublicKey()
{
    # Regenerate player's system public key.
    echo "y" | ssh-keygen -t ecdsa -N "" -q -f  /etc/ssh/ssh_host_rsa_key >/dev/null 2>&1
}


function System_setup()
{
    if [ ! -d /etc/player ]; then
        mkdir /etc/player
    fi

    echo "$ORCHESTRATOR_ADDRESS" > /etc/player/orchestrator.address
    echo "$ORCHESTRATOR_PASSWORD" > /etc/player/orchestrator.password
    echo "$PLAYER_NAME" > /etc/player/name
    echo "$PLAYER_POSITION" > /etc/player/position
    echo "$PLAYER_COMMENT" > /etc/player/comment
}


function System_playerServiceInstall()
{
    cat > /usr/bin/player.sh<<'EOF'
#!/bin/bash

orchestratorUrl="https://$(echo -n $(cat /etc/player/orchestrator.address))/backend/api/v1/backend/players/"
orchestratorPassword="$(echo -n $(cat /etc/player/orchestrator.password))"

uuid="$(echo -n $(ip -o link show | grep -oP '(?<=ether ).*(?=$)' | tail -1 | sed 's/brd.*//g' | sed 's/ //g' | sed 's/://g'))"
playerType="slideshow"
name="$(echo -n $(cat /etc/player/name))"
position="$(echo -n $(cat /etc/player/position))"
address="$(echo -n $(ip a | grep 'inet ' | grep -v 'host lo' | tail -1 | grep -oP '(?<=inet ).*(?=/24)'))"
comment="$(echo -n $(cat /etc/player/comment))"
metrics="$(echo -n uptime: $(uptime | grep -oP '(<?up).*(?=,)' | awk -F',' '{print $1}' | sed 's/ //g' | sed 's/up//g'))"

sshPublicKey="$(echo -n $(cat /etc/ssh/ssh_host_rsa_key.pub))"
curl --insecure -u admin:${orchestratorPassword} ${orchestratorUrl} --header 'Content-Type: application/json' --data \
"{
    \"data\": {
        \"uuid\": \"${uuid}\",
        \"player_type\": \"${playerType}\",
        \"name\": \"${name}\",
        \"position\": \"${position}\",
        \"address\": \"${address}\",
        \"comment\": \"${comment}\",
        \"metrics\": \"${metrics}\",
        \"ssh_public_key\": \"${sshPublicKey}\"
    }
}" > /tmp/orchestrator.response 2>/dev/null

if [ ! -d /root/.ssh ]; then
    mkdir /root/.ssh
fi

touch /root/.ssh/authorized_keys

# Save returned orchestrator key into authorized keys, if not present.
k=$(cat /tmp/orchestrator.response | jq '. | .data.orchestrator_ssh_public_key' | sed  's/"//g')
if ! grep -q "$k" /root/.ssh/authorized_keys; then
    echo "Saving Orchestrator SSH public key into known hosts..."
    echo "$k" >> /root/.ssh/authorized_keys
fi

exit 0
EOF
    chmod +x /usr/bin/player.sh

    cat > /etc/systemd/system/player.service<<'EOF'
[Unit]
Description=Player service

[Service]
Type=idle
RemainAfterExit=no
KillMode=process
ExecStart=player.sh

StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=player

[Install]
WantedBy=multi-user.target
EOF

    cat >/etc/systemd/system/player.timer<<'EOF'
[Unit]
Description=Run Player service every minute
Requires=player.service

[Timer]
Unit=player.service
OnCalendar=*-*-* *:*:30
AccuracySec=1us

[Install]
WantedBy=timers.target
EOF

    systemctl daemon-reload
    systemctl enable player.service
    systemctl restart player.service

    systemctl enable player.timer
    systemctl restart player.timer
}

# ##################################################################################################################################################
# Main
# ##################################################################################################################################################

ACTION=""
ORCHESTRATOR_ADDRESS=""
ORCHESTRATOR_PASSWORD=""
PLAYER_NAME=""
PLAYER_POSITION=""
PLAYER_COMMENT=""

# Must be run as root.
ID=$(id -u)
if [ $ID -ne 0 ]; then
    echo "This script needs root powers."
    exit 1
fi

# Parse user input.
while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
        --action)
            ACTION="$2"
            shift
            shift
            ;;

        --orchestrator-address)
            ORCHESTRATOR_ADDRESS="$2"
            shift
            shift
            ;;

        --orchestrator-password)
            ORCHESTRATOR_PASSWORD="$2"
            shift
            shift
            ;;

        --player-name)
            PLAYER_NAME="$2"
            shift
            shift
            ;;

        --player-position)
            PLAYER_POSITION="$2"
            shift
            shift
            ;;

        --player-comment)
            PLAYER_COMMENT="$2"
            shift
            shift
            ;;

        *)
            shift
            ;;
    esac
done

if [ -z "$ACTION" ] || [ -z "$ORCHESTRATOR_ADDRESS" ] || [ -z "$ORCHESTRATOR_PASSWORD" ] || [ -z "$PLAYER_NAME" ]; then
    echo "Missing parameters. Use --action install --orchestrator-address IP_OR_FQDN --orchestrator-password PASSWORD --player-name NAME --player-position OPTIONAL_POSITION_NOTES --player-comment OPTIONAL_COMMENT"
else
    System "system"
    $system_run
fi

exit 0