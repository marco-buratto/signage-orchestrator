**DEBUGGING SIGNAGE ORCHESTRATOR PLATFORM** 

***Players connection debug***

After the installation and players/orchestrator coupling procedure completes, any player should be enlisted in the Orchestrator Players tab.
If not, there's an error somewhere: try launching the connection script manually (within the same malfunctioning player, of course as root):

    sed -i 's|/tmp/orchestrator.response 2>/dev/null|/tmp/orchestrator.response|g' /usr/bin/player.sh
    /usr/bin/player.sh

On network or any fatal error (if any), you could now see the details.

If otherwise no error is displayed, you can see the Orchestrator response with:

    cat /tmp/orchestrator.response | jq

If something like:

    {
        "data": {
           "orchestrator_ssh_public_key": "ecdsa-sha2-nistp256 ... root@orchestratorTest"
        } 
    }

is displayed, the communication is ok, so the player *is* correctly connected to the Orchestrator. Re-check all the installation/coupling steps if the player is still not visible on the Orchestrator GUI.

------------

***Connection ok, but nothing happens on the player***

Re-checking here all the necessary steps on the Orchestrator (with Slideshow player types as example).
1. the Player must be in a group;
2. create a slideshow playlist, for example with just one media.conf directive inside:

       url: https://www.binaryemotions.com/wp-content/uploads/2021/06/digital-signage.jpg
3. in the Events tab, schedule an event: select a group of players on top left, insert an event into the timetable and add the playlist to it.

If all the previous steps have been followed correctly, everything should function as intended.
For any other debug on the player, try having a look at the syslog:

    apt install rsyslog
    tail -f /var/log/syslog # see the output when you expect a player to change its state.

Correct behaviour entries are:

    raspberry-slideshow systemd[1]: Started player.service - Player service.
    raspberry-slideshow systemd[1]: player.service: Deactivated successfully.

------------

***Debugging the Orchestrator***

Orchestrator-side, we can see if, how and when the server communicates with the players with:

    # SSH in as root.
    tail -f /var/log/syslog

A normal output looks like:

    DJANGO_API - ________________________________________________________________________________
    DJANGO_API - List of Event
    DJANGO_API - ________________________________________________________________________________
    DJANGO_API - --> Response: <Response status_code=200, "application/json">
    APACHE_ACCESS_API: 2024-03-15 22:30:00.165 api:80 127.0.0.1 - admin "-" "GET /api/v1/backend/events/?loadGroup=true&loadPlaylist=true&start_date=2024-03-15%2022%3A30 HTTP/1.1" 200 1338 "-" "curl/7.88.1"
    systemd[1]: orchestrator.service: Deactivated successfully.
    root: Processing 192.168.0.118: configuring and starting Raspberry Slideshow...
