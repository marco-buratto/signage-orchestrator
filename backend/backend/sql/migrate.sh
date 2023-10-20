#!/bin/bash

# Migration scripts naming convention: yyyy-mm-gg-name.sql.

for f in /var/www/backend/backend/sql/diff/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-*.sql; do
    if [ -f "$f" ]; then
        diff="$(echo $f | grep -oP '(?<=diff/).*(?=$)')" # diff name.

        echo -n "Checking if $diff has already been applied... "
        res="$(mysql --vertical -e "SELECT * FROM api.migrations WHERE name = '$diff';" | grep sql)"
        if [ "$res" != "" ]; then
            echo "applied."
        else
            echo -n "not applied: updating database... "

            mysql api -e "source $f;"
            if [ $? -eq 0 ]; then
                # Insert migration name in database, if done.
                mysql -e "INSERT INTO api.migrations (name) VALUES ('$diff');"
                if [ $? -eq 0 ]; then
                    echo "Done."
                else
                    echo "Error."
                fi
            fi
        fi
    fi
done

exit 0
