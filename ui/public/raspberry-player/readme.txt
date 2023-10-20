Player connector usage

SSH
sudo -i
wget --no-check-certificate https://ORCHESTRATOR_ADDRESS/raspberry-player/player-connector.sh # @todo: --insecure
bash player-connector.sh --action install --orchestrator-address ORCHESTRATOR_ADDRESS --orchestrator-password ORCHESTRATOR_PASSWORD --player-name NAME --player-position OPTIONAL_POSITION_NOTES --player-comment OPTIONAL_COMMENT
    example: bash player-connector.sh --action install --orchestrator-address 10.0.120.200 --orchestrator-password password --player-name Slideshow.1 --player-position "--" --player-comment "Just a comment"
