#!/bin/bash

# Load events which fire now and command the involved players.

stopEventsSource="/tmp/stop-events.list"
startEventsSource="/tmp/start-events.list"
now="$(date '+%Y-%m-%d %H:%M' | sed 's/ /%20/g' | sed 's/:/%3A/g')" # url encoded.
orchestratorPassword="$(cat /etc/orchestrator.password)"

if [ -f /etc/orchestrator.password ]; then
    # Stop events which fire now.
    orchestratorUrl="http://localhost:8000/api/v1/backend/events/?loadGroup=true&loadPlaylist=false&end_date=${now}"

    curl --request GET -u admin:${orchestratorPassword} ${orchestratorUrl} > ${stopEventsSource} 2>/dev/null

    eventsNumber=$(cat ${stopEventsSource} | jq '. | .data.count')
    if [ ${eventsNumber} -gt 0 ]; then
        for event in $(seq 0 $((${eventsNumber}-1))); do
            playersNumber=$(cat ${stopEventsSource} | jq ". | .data.items[${event}].group.players_count")
            for player in $(seq 0 $((${playersNumber}-1))); do
                (
                    address=$(cat ${stopEventsSource} | jq ". | .data.items[${event}].group.players[${player}].address" | sed 's/\"//g')

                    echo "Processing ${address}: stopping Raspberry Slideshow..."
                    su - www-data -c "ssh root@${address} systemctl stop rs"
                    su - www-data -c "ssh root@${address} tty1cleanup.sh"

                    exit 0
                ) &
            done
        done
    fi

    # Start events which fire now.
    orchestratorUrl="http://localhost:8000/api/v1/backend/events/?loadGroup=true&loadPlaylist=true&start_date=${now}"
    curl --request GET -u admin:${orchestratorPassword} ${orchestratorUrl} > ${startEventsSource} 2>/dev/null

    eventsNumber=$(cat ${startEventsSource} | jq '. | .data.count')
    if [ ${eventsNumber} -gt 0 ]; then
        for event in $(seq 0 $((${eventsNumber}-1))); do
            playersNumber=$(cat ${startEventsSource} | jq ". | .data.items[${event}].group.players_count")
            for player in $(seq 0 $((${playersNumber}-1))); do
                (
                    address=$(cat ${startEventsSource} | jq ". | .data.items[${event}].group.players[${player}].address" | sed 's/\"//g')
                    mediaconf=$(cat ${startEventsSource} | jq ". | .data.items[${event}].playlist.mediaconf" | sed 's/\"//g')
                    transition=$(cat ${startEventsSource} | jq ". | .data.items[${event}].playlist.transition")
                    blend=$(cat ${startEventsSource} | jq ". | .data.items[${event}].playlist.blend")

                    echo "Processing ${address}: configuring and starting Raspberry Slideshow..."
                    su - www-data -c "ssh root@${address} systemctl stop rs"
                    su - www-data -c "ssh root@${address} \"echo ${mediaconf} > /tmp/media.conf.tmp.base64; base64 --decode /tmp/media.conf.tmp.base64 > /var/lib/rs/media.conf\""
                    su - www-data -c "ssh root@${address} sed -i \"s/TRANSITION_TIME_S=.*/TRANSITION_TIME_S=${transition}/g\" /etc/rs.conf" >/dev/null 2>&1 || true
                    su - www-data -c "ssh root@${address} sed -i \"s/BLEND_TIME_MS=.*/BLEND_TIME_MS=${blend}/g\" /etc/rs.conf" >/dev/null 2>&1 || true
                    su - www-data -c "ssh root@${address} systemctl restart rs"

                    exit 0
                ) &
            done
        done
    fi
fi

exit 0