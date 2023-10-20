#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 vm_name start|stop"
    exit 1
fi

function start() {
    echo "$0: set fs.inotify.max_user_watches"
    if ! sudo /usr/sbin/sysctl -w fs.inotify.max_user_watches=524288; then
        echo "Failed to set fs.inotify.max_user_watches"
    fi
}

function stop() {
    vmName="$1"
    # List the other vms that need fsnotify. Reset only if there are not powered on vm in the list.
    vmList=$(grep -B1 'trigger.name = "fsnotify: restore' Vagrantfile | grep 'trigger.after :halt' | awk -F'.' '{print $1}' | grep -v "$vmName")
    vmUp=$(for vm in $vmList; do vagrant status $vm | grep -E "^${vm}[[:space:]]+running"; done)
    if [ -z "$vmUp" ]; then
        echo "$0: reset fs.inotify.max_user_watches to the default value"
        if ! sudo /usr/sbin/sysctl -w fs.inotify.max_user_watches=8192; then
            echo "Failed to reset fs.inotify.max_user_watches"
        fi
    fi
}


case "$2" in
        start)
            start
            ;;

        stop)
            stop "$1"
            ;;

        *)
            echo "Usage: $0 vm_name start|stop"
            exit 1

esac
