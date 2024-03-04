#!/bin/bash

ADMIN="postgres"
DATABASE="benjamindavies_api"
USER="api_tester"
PASSWORD="recipe"


# LINUX
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # starts service if not running
    sudo service postgresql start
    
    # Create the database
    sudo -u $ADMIN psql -c "CREATE DATABASE $DATABASE;"

    # Create the new user and grant permissions
    sudo -u $ADMIN psql -c "CREATE USER $USER WITH ENCRYPTED PASSWORD '$PASSWORD';"
    sudo -u $ADMIN psql -c "GRANT ALL PRIVILEGES ON DATABASE $DATABASE TO $USER;"
    
    # So you dont run into any access problems
    sudo -u $ADMIN psql -c "ALTER DATABASE $DATABASE OWNER TO $USER;"

    echo "Database '$DATABASE' and user '$USER' created successfully with all permissions granted."




# MAC OS
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # starts service if not running
    brew services start postgresql
    
    # create new database 
    sudo -u $ADMIN createdb $DATABASE

    # Create the new user and grant permissions
    sudo -u $ADMIN psql -c "CREATE USER $USER WITH ENCRYPTED PASSWORD '$PASSWORD';"
    sudo -u $ADMIN psql -c "GRANT ALL PRIVILEGES ON DATABASE $DATABASE TO $USER;"
    
    # So you dont run into any access problems
    sudo -u $ADMIN psql -c "ALTER DATABASE $DATABASE OWNER TO $USER;"

    echo "Database '$DATABASE' and user '$USER' created successfully with all permissions granted."
else {
    echo "Sorry your operating system isn't compatable please manually create the database"
}
fi