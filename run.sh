#!/bin/bash

ADMIN="postgres"
DATABASE="benjamindavies_api"
USER="api_tester"
PASSWORD="recipe"



if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo service postgresql start
    # Create the database
    sudo -u $ADMIN psql -c "CREATE DATABASE $DATABASE;"

    # Create the new user and grant permissions
    sudo -u $ADMIN psql -c "CREATE USER $USER WITH ENCRYPTED PASSWORD '$PASSWORD';"
    sudo -u $ADMIN psql -c "GRANT ALL PRIVILEGES ON DATABASE $DATABASE TO $USER;"

    echo "Database '$DATABASE' and user '$USER' created successfully with all permissions granted."

elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew services start postgresql
    sudo -u $ADMIN createdb $DATABASE

    # Create the new user and grant permissions
    sudo -u $ADMIN psql -c "CREATE USER $USER WITH ENCRYPTED PASSWORD '$PASSWORD';"
    sudo -u $ADMIN psql -c "GRANT ALL PRIVILEGES ON DATABASE $DATABASE TO $USER;"

    echo "Database '$DATABASE' and user '$USER' created successfully with all permissions granted."
else 
    echo Sorry your system isn't compatible you will have to manually add the database
fi