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
        System_definitions
        System_cleanup

        System_systemFilesSetup
        System_debianFilesSetup

        System_codeCollect
        System_codeConfig
        System_codeFilesPermissions
        System_venv
        System_fixDebVersion

        System_debCreate
        System_cleanup

        echo "Created /tmp/$projectName.deb"
    fi
}

# ##################################################################################################################################################
# Private static
# ##################################################################################################################################################

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

    projectName="signage-orchestrator-backend_${debPackageRelease}_all"
    workingFolder="/tmp"
    workingFolderPath="${workingFolder}/${projectName}"
}


function System_cleanup()
{
    if [ -n "$workingFolderPath" ]; then
        if [ -d "$workingFolderPath" ]; then
            rm -fR "$workingFolderPath"
        fi
    fi
}


function System_codeCollect()
{
    mkdir -p $workingFolderPath/var/www/backend
    mkdir -p $workingFolderPath/var/lib/api-venv

    # Copy files.
    cp -R api $workingFolderPath/var/www/backend
    cp -R backend $workingFolderPath/var/www/backend
    cp license.txt $workingFolderPath/var/www/backend

    # Remove __pycache__ folders and not-required ones.
    rm -fR $workingFolderPath/var/www/backend/backend/tests
    rm -fR $(find $workingFolderPath/var/www/backend -name __pycache__)
}


function System_codeConfig()
{
    # Production settings.
    sed -i "s/^DEBUG =.*/DEBUG = False/g" $workingFolderPath/var/www/backend/api/settings.py

    # The following settings are emptied here and filled-in by postinst/s (debconf).
    sed -i "s/^SECRET_KEY =.*/SECRET_KEY = \"1234567890\"/g" $workingFolderPath/var/www/backend/api/settings.py
    sed -i "s/^ALLOWED_HOSTS =.*/ALLOWED_HOSTS = ['*']/g" $workingFolderPath/var/www/backend/api/settings.py
}


function System_codeFilesPermissions()
{
    # Forcing standard permissions (755 for folders, 644 for files, owned by www-data:www-data).
    chown -R www-data:www-data $workingFolderPath/var/www/backend
    find $workingFolderPath/var/www/backend -type d -exec chmod 0750 {} \;
    find $workingFolderPath/var/www/backend -type f -exec chmod 0640 {} \;

    chmod 400 $workingFolderPath/etc/apache2/default.*

    # Particular permissions.
    #resources=( "workingFolderPath/var/www/backend" )
    #for res in "${resources[@]}"; do
    #    find $res -type d -exec chmod 750 {} \;
    #    find $res -type f -exec chmod 640 {} \;
    #done
}


function System_venv()
{
    # Put all pip dependencies in a virtual env.
    # All dependencies will be then included in the .deb package; Apache virtual host is set up accordingly.
    cp api/pip.requirements $workingFolderPath/var/lib/api-venv

    # Start virtual environment for the collection of the dependencies.
    cd $workingFolderPath
    python3 -m venv var/lib/api-venv
    source var/lib/api-venv/bin/activate

    # Install pip dependencies in the virtual environment.
    python -m pip install --upgrade pip
    python -m pip install -r var/lib/api-venv/pip.requirements
    python -m pip list --format=freeze > /tmp/pip.freeze.venv # Workaround: see https://stackoverflow.com/questions/62885911/pip-freeze-creates-some-weird-path-instead-of-the-package-version

    # Exit from the virtual env.
    deactivate
    cd -

    rm $workingFolderPath/var/lib/api-venv/pip.requirements

    # Removing cached information within the venv (--> cleanup the venv).
    rm -R $(find $workingFolderPath/var/lib/api-venv/ -name __pycache__)
    sed -i "s|$workingFolderPath||g" $(grep -iR $workingFolderPath $workingFolderPath/var/lib/api-venv/ | awk -F: '{print $1}')

    # Configure the app.
    # Add the PATH the bin folder of the python venv.
    API_VENV='/var/lib/api-venv'
    sed -i -r -e "s#VENV_BIN =.*#VENV_BIN = \"${API_VENV}/bin/\"#" $workingFolderPath/var/www/backend/api/settings.py
}


function System_fixDebVersion()
{
    debVer=`echo $debPackageRelease | awk -F'-' '{print $1'}`
    if [ -r api/pip.lock ]; then
        SameVer="y"
        for pyPack in $(cat /tmp/pip.freeze.venv | awk -F'==' '{print $1}'); do
            # Get version from new freeze file.
            nVer=$(cat /tmp/pip.freeze.venv | grep -E "^$pyPack==" | awk -F'==' '{print $2}')
            # Get version from old freeze file.
            if grep -Eq "^$pyPack==" api/pip.lock; then
                oVer=$(cat api/pip.lock | grep -E "^$pyPack==" | awk -F'==' '{print $2}')
            else
                oVer='missing'
            fi

            if [ "$nVer" != "$oVer" ]; then
                SameVer="n"
                echo -e "Package \e[92m${pyPack}\e[0m have a different version than before: old: $oVer, new: $nVer"
            fi
        done

        if [ "$SameVer" != "y" ]; then
            echo "Overwriting pip.lock file..."
            cp /tmp/pip.freeze.venv api/pip.lock
            echo "Some python package version changed, please update debian version file."
        else
            echo "Versions of the python packages are not changed."
        fi
    else
        echo "File pip.lock was not present."
        cp /tmp/pip.freeze.venv api/pip.lock
    fi
}


function System_systemFilesSetup()
{
    # Create a new working folder.
    mkdir $workingFolderPath

    # Setting up system files.
    cp -R DEBIAN-PKG/etc $workingFolderPath
    cp -R DEBIAN-PKG/usr $workingFolderPath

    find $workingFolderPath -type d -exec chmod 0755 {} \;
    find $workingFolderPath -type f -exec chmod 0644 {} \;

    chmod +x $workingFolderPath/usr/bin/orchestrator.sh
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
