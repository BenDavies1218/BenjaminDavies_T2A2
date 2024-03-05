#!/bin/bash

ADMIN="postgres"
DATABASE="benjamindavies_api"
USER="api_tester"
PASSWORD="recipe"

EXISTING_DATABASE=$(sudo -u $ADMIN psql -t -A -c "SELECT 1 FROM pg_database WHERE datname='$DATABASE';")

# LINUX
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [ -z "$EXISTING_DATABASE" ]; then

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
        
        
    else
        
        sudo -u $ADMIN psql -c "DROP DATABASE $DATABASE"
        sudo -u $ADMIN psql -c "DROP USER $USER"

        echo "Database '$DATABASE' and user '$USER'  have been successfully deleted"
    fi


# MAC OS
elif [[ "$OSTYPE" == "darwin"* ]]; then
    if [ -z "$EXISTING_DATABASE" ]; then
        
        # Start PostgreSQL service if not running
        brew services start postgresql
    
        # create new database
        sudo -u $ADMIN createdb $DATABASE

        # Create the new user and grant permissions
        sudo -u $ADMIN psql -c "CREATE USER $USER WITH ENCRYPTED PASSWORD '$PASSWORD';"
        sudo -u $ADMIN psql -c "GRANT ALL PRIVILEGES ON DATABASE $DATABASE TO $USER;"
        
        # So you dont run into any access problems
        sudo -u $ADMIN psql -c "ALTER DATABASE $DATABASE OWNER TO $USER;"

        echo "Database '$DATABASE' and user '$USER' created successfully with all permissions granted."
    else
        
        sudo -u $ADMIN psql -c "DROP DATABASE $DATABASE"
        sudo -u $ADMIN psql -c "DROP USER $USER"

        echo "Database '$DATABASE' and user '$USER'  have been successfully deleted"
    fi

else {
    echo "Sorry your operating system isn't compatable or postgres user doen't exist / isn't authorized to do this, please manually create the database"
}
fi