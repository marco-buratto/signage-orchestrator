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
    PROXY="$PROXY"

    DATABASE_USER_PASSWORD="password"
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
        if System_checkEnvironment; then
            printf "\n* Installing system...\n"
            echo "This script requires a fresh-installation of Debian 12/Bookworm..."

            System_proxySet "$PROXY"
            System_installDependencies
            System_pythonSetup
            System_mariadbSetup "$DATABASE_USER_PASSWORD"
            System_apacheSetup "$DATABASE_USER_PASSWORD"
            System_pipInstallDaemon_api
        else
            echo "A Debian Bookworm operating system is required for the installation. Aborting."
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
        if ! grep -qi 'Debian GNU/Linux 12 (bookworm)' /etc/os-release; then
            return 1
        fi
    else
        return 1
    fi

    return 0
}



function System_proxySet()
{
    printf "\n* Setting up system proxy...\n"

    if ! grep -qi "http_proxy" /etc/environment; then
        echo "http_proxy=$1" >> /etc/environment
        echo "https_proxy=$1" >> /etc/environment
    else
        sed -i "s|http_proxy=.*|http_proxy=$1|g" /etc/environment
        sed -i "s|https_proxy=.*|https_proxy=$1|g" /etc/environment
    fi

    export http_proxy=$1
    export https_proxy=$1
}



function System_installDependencies()
{
    printf "\n* Preparing the environment: removing the cdrom entry in apt/sources.list, if present...\n"
    printf "\n* Installing system dependencies...\n"

    if [ -r /tmp/sources.list ]; then
        cp -f /tmp/sources.list /etc/apt/sources.list
    fi

    apt update
    apt install -y wget git unzip net-tools dnsutils dos2unix curl vim openssh-client ntp # base.
    apt install -y python3-pip python3-dev # base python + dev.
    apt install -y python3-venv # for making the .deb.
    apt install -y mariadb-server libmariadb-dev # mariadb server + dev (for the mysqlclient pip package).
    apt install -y php8.2-mysql php8.2-mbstring # php and php for mysql.
    apt install -y libapache2-mod-php8.2 libapache2-mod-wsgi-py3 # apache for php and python.
    apt install -y redis-server # redis.

    apt clean
    
    printf "\n* Regenerate system SSH keypair...\n"
    echo "y" | ssh-keygen -t ecdsa -N '' -q -f /etc/ssh/ssh_host_rsa_key > /dev/null
    
}



function System_pythonSetup()
{
    printf "\n* Installing pip dependencies...\n"
	
    update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1 # best practice for simply creating a symlink.

    # pip Requirements files are used to hold the result from pip freeze for the purpose of achieving repeatable installations.
    # In this case, your requirement file contains a pinned version of everything that was installed when pip freeze was run.
    # pip freeze > requirements.txt
    # pip install -r requirements.txt

    # Requirement Specifiers
    # SomeProject
    # SomeProject == 1.3
    # SomeProject >=1.2,<2.0
    # SomeProject[foo, bar]
    # SomeProject~=1.4.2

    pip install --break-system-packages --upgrade pip
    pip install --break-system-packages -r /var/www/backend/api/pip.requirements # pip install requirements.
}



function System_mariadbSetup()
{
    printf "\n* Setting up MariaDB: user api...\n"

    databaseUserPassword=$1
    if mysql -e "exit" >/dev/null 2>&1; then
        if [ "$(mysql --vertical -e "SELECT User FROM mysql.user WHERE User = 'api';" | tail -1 | awk '{print $2}')" == "" ]; then
            # User api not present: create.
            mysql -e "CREATE USER 'api'@'%' IDENTIFIED BY '$databaseUserPassword';"
        else
            # Update user's password.
            mysql -e "SET PASSWORD FOR 'api'@'%' = PASSWORD('$databaseUserPassword');"
        fi
    else
        echo "MariaDB error: shell access disabled."
        exit 1
    fi
}



function System_apacheSetup()
{
    printf "\n* Setting up Apache...\n"

    cd /tmp

    # /var/www/backend is mounted by Vagrant (share), here lays the Django stub project.
    if [ ! -d /var/www/backend ]; then
        echo "/var/www/backend does not exist, check your Vagrant setup."
        exit 1
    fi

    # Copy phpMyAdmin files.
    if [ ! -f phpMyAdmin-5.1.3-all-languages.zip ]; then
        wget https://files.phpmyadmin.net/phpMyAdmin/5.1.3/phpMyAdmin-5.1.3-all-languages.zip
    fi

    unzip phpMyAdmin-5.1.3-all-languages.zip >/dev/null

    if [ -d /var/www/myadmin ]; then
        rm -fr var/www/myadmin
    fi

    mv phpMyAdmin-5.1.3-all-languages /var/www/myadmin
    chown -R www-data:www-data /var/www/myadmin

    # Configure phpMyAdmin for direct login.
    sed -i "s/\$cfg\['Servers'\]\[\$i\]\['auth_type'\].*/\$cfg\['Servers'\]\[\$i\]\['auth_type'\] = 'config';/g" /var/www/myadmin/libraries/config.default.php
    sed -i "s/\$cfg\['Servers'\]\[\$i\]\['user'\].*/\$cfg\['Servers'\]\[\$i\]\['user'\] = 'api';/g" /var/www/myadmin/libraries/config.default.php
    sed -i "s/\$cfg\['Servers'\]\[\$i\]\['password'\].*/\$cfg\['Servers'\]\[\$i\]\['password'\] = '$1';/g" /var/www/myadmin/libraries/config.default.php

    # Setup the Django project virtual host.
    # Static content has been moved from rest_framework to static/ via the use of python manage.py collectstatic.
    cp -f /vagrant/backend/etc/apache2/sites-available/001-django.conf /etc/apache2/sites-available/001-django.conf
    chmod 644 /etc/apache2/sites-available/001-django.conf

    # Setup the phpMyAdmin virtual host on port 8000.
    cp -f /vagrant/backend/etc/apache2/sites-available/001-mysql.conf /etc/apache2/sites-available/001-mysql.conf
    chmod 644 /etc/apache2/sites-available/001-mysql.conf

    # This is a trick in order for Apache not to need to be reloaded at every .py modification.
    if ! grep -q "MaxRequestsPerChild" /etc/apache2/apache2.conf; then
        printf "\nMaxRequestsPerChild 1\n" >> /etc/apache2/apache2.conf
    fi

    # Configure www-data user.
    usermod --shell /bin/bash www-data # enabling shell capabilities for the httpd user.

    mkdir /var/www/.ssh # used for players' known keys.
    touch /var/www/.ssh/known_hosts
    echo "y" | ssh-keygen -t ecdsa -N '' -q -f /var/www/.ssh/id_ecdsa > /dev/null # generating www-data SSH keypair.
    chown -R www-data:www-data /var/www/.ssh/

    # Force enabling the wsgi module.
    a2enmod wsgi

    a2query -s 000-default && a2dissite 000-default # disable default Apache site, only if enabled.
    
    if ! grep -q '^Listen 8000$' /etc/apache2/ports.conf; then
        echo "Listen 8000" >> /etc/apache2/ports.conf
    fi

    # Setup Apache config files for its virtualhosts.
    a2ensite 001-django
    a2ensite 001-mysql
    a2query -s 000-default && a2dissite 000-default # disable default site, only if enabled.

    systemctl restart apache2
}



System_pipInstallDaemon_api()
{
    printf "\n* Setting up Systemd service for installing pip dependencies from project's requirements file...\n"

    # pip install service.
    cp -f /vagrant/backend/etc/systemd/system/pip_install_api.service /etc/systemd/system/pip_install_api.service
    chmod 644 /etc/systemd/system/pip_install_api.service

    # Watchdog service: monitor folder for changes.
    cp -f /vagrant/backend/etc/systemd/system/pip_install_api.path /etc/systemd/system/pip_install_api.path
    chmod 644 /etc/systemd/system/pip_install_api.path

    systemctl daemon-reload
    systemctl enable systemd-networkd.service systemd-networkd-wait-online.service

    systemctl enable pip_install_api.path
    systemctl enable pip_install_api.service
    systemctl restart pip_install_api.path
}



# ##################################################################################################################################################
# Main
# ##################################################################################################################################################

ACTION=""
PROXY=""

# Must be run as root (sudo).
ID=$(id -u)
if [ $ID -ne 0 ]; then
    echo "This script needs super cow powers."
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

        --proxy)
            PROXY="$2"
            shift
            shift
            ;;

        *)
            shift
            ;;
    esac
done

if [ -z "$ACTION" ]; then
    echo "Missing parameters. Use --action install for installation."
else
    System "system"
    $system_run
fi

exit 0

