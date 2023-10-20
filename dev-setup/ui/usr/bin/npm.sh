#!/bin/bash

function start() {
    cd /var/www/ui
    setsid bash -c 'exec su - vagrant -c "export NODE_OPTIONS=--openssl-legacy-provider && cd /var/www/ui && npm run dev -- --host | logger -t npm" <> /dev/tty2 >&0 2>&1' >> /home/vagrant/npm.log & # attach npm to tty2; otherwise it is killed by Systemd.
}

function stop() {
    PS=$(ps axu|grep -P 'node|react|npm' | grep -Pv 'grep|npm.sh' | awk '{print $2}')
    if [ -n "$PS" ]; then
        kill $PS
    fi
}

function status() {
    PS=$(ps axu|grep 'node' | grep -v grep | awk '{print $2}')
    if [ -n "$PS" ]; then
        echo "Service running"
    else
        echo "Service not running"
    fi
}

function restart() {
    stop
    sleep .5
    start
}

case $1 in
        start)
            start
            ;;

        stop)
            stop
            ;;

        restart)
            stop
            start
            ;;

        *)
            echo $"Usage: $0 {start|stop|restart}"
            exit 1

esac

exit 0
