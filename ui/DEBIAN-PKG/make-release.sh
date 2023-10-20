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
}

# ##################################################################################################################################################
# Public
# ##################################################################################################################################################

#
# Void System_run().
#
function System_run()
{
    if [ "$ACTION" == "deb" ]; then
        if System_checkEnvironment; then
            System_definitions
            System_cleanup

            System_systemFilesSetup
            System_debianFilesSetup

            System_webpack
            System_codeConfig
            System_codeCollect
            System_codeFilesPermissions

            System_debCreate
            System_cleanup

            echo "Created /tmp/$projectName.deb"
        else
            echo "A Debian Bullseye operating system is required for the deb-ification. Aborting."
            exit 1
        fi
    else
        exit 1
    fi
}

# ##################################################################################################################################################
# Private static
# ##################################################################################################################################################

function System_checkEnvironment()
{
    if [ -f /etc/os-release ]; then
        if ! grep -q 'Debian GNU/Linux 11 (bullseye)' /etc/os-release; then
            return 1
        fi
    else
        return 1
    fi

    return 0
}


function System_definitions()
{
    declare -g debPackageRelease

    declare -g projectName
    declare -g workingFolder
    declare -g workingFolderPath

    if [ -f DEBIAN-PKG/deb.release ]; then
        # Get program version from the release file.
        debPackageRelease=$(echo $(cat DEBIAN-PKG/deb.release))
    else
        echo "Error: deb.release missing."
        echo "Usage: bash DEBIAN-PKG/make-release.sh --action deb"
        exit 1
    fi

    projectName="signage-orchestrator-ui_${debPackageRelease}_all"
    workingFolder="/tmp"
    workingFolderPath="${workingFolder}/${projectName}"
}


function System_cleanup()
{
    if [ -n "$workingFolderPath" ]; then
        if [ -d dist ]; then
            rm -fR dist
        fi

        if [ -d "$workingFolderPath" ]; then
            rm -fR "$workingFolderPath"
        fi
    fi
}


function System_webpack()
{
    npm run build
}


function System_codeConfig()
{
    # Production settings.
    sed -i 's|config.globalProperties.backendUrl=".*backend/";|config.globalProperties.backendUrl="/backend/api/v1/backend/";|g' dist/assets/*.js
}


function System_codeCollect()
{
    mkdir -p $workingFolderPath/var/www

    # Copy files.
    mv dist $workingFolderPath/var/www/ui
}


function System_codeFilesPermissions()
{
    # Forcing standard permissions (755 for folders, 644 for files, owned by www-data:www-data).
    chown -R www-data:www-data $workingFolderPath/var/www/ui
    find $workingFolderPath/var/www/ui -type d -exec chmod 0750 {} \;
    find $workingFolderPath/var/www/ui -type f -exec chmod 0640 {} \;
}


function System_systemFilesSetup()
{
    # Create a new working folder.
    mkdir $workingFolderPath

    # Setting up system files.
    if [ -d DEBIAN-PKG/etc ]; then
        cp -R DEBIAN-PKG/etc $workingFolderPath

        find $workingFolderPath -type d -exec chmod 0755 {} \;
        find $workingFolderPath -type f -exec chmod 0644 {} \;
    fi
}


function System_debianFilesSetup()
{
    # Setting up all the files needed to build the package (DEBIAN folder).
    cp -R DEBIAN-PKG/DEBIAN $workingFolderPath

    sed -i "s/^Version:.*/Version:\ $debPackageRelease/g" $workingFolderPath/DEBIAN/control

    if [ -f $workingFolderPath/DEBIAN/preinst ]; then
        chmod +x $workingFolderPath/DEBIAN/preinst
    fi
    if [ -f $workingFolderPath/DEBIAN/postinst ]; then
        chmod +x $workingFolderPath/DEBIAN/postinst
    fi
    if [ -f $workingFolderPath/DEBIAN/prerm ]; then
        chmod +x $workingFolderPath/DEBIAN/prerm
    fi
    if [ -f $workingFolderPath/DEBIAN/postrm ]; then
        chmod +x $workingFolderPath/DEBIAN/postrm
    fi
}


function System_debCreate()
{
    cd $workingFolder
    dpkg-deb --build $projectName
}

# ##################################################################################################################################################
# Main
# ##################################################################################################################################################

ACTION=""

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

        *)
            shift
            ;;
    esac
done

if [ -z "$ACTION" ]; then
    echo "Missing parameters. Use --action deb."
else
    System "system"
    $system_run
fi

exit 0
