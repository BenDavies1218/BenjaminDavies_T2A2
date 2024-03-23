#!/bin/bash

# information for the database including superuser, db name, db user, user password
# if your superuser isn't postgres then you may be able to just change the variable to your local superuser
ADMIN="postgres"
DATABASE="benjamindavies_api"
USER="api_tester"
PASSWORD="recipe"

# checks if the database exists
EXISTING_DATABASE=$(sudo -u $ADMIN psql -t -A -c "SELECT 1 FROM pg_database WHERE datname='$DATABASE';")

# LINUX
# checks the OS type before trying
if [[ "$OSTYPE" == "linux-gnu"* ]]; then

    # If the database doesn't exist than we create one
    if [ -z "$EXISTING_DATABASE" ]; then

    # Activate Virtual Enviroment
        echo Activating virtual Enviroment 
        python3 -m venv .venv
        source .venv/bin/activate
        echo $VIRTUAL_ENV


        # Install Packages
        echo Installing External Packages
        pip3 install -r requirements.txt

        # starts a postgres service
        sudo service postgresql start

        # Create the database
        sudo -u $ADMIN psql -c "CREATE DATABASE $DATABASE;"

        # Create the new user and grant permissions
        sudo -u $ADMIN psql -c "CREATE USER $USER WITH ENCRYPTED PASSWORD '$PASSWORD';"
        sudo -u $ADMIN psql -c "GRANT ALL PRIVILEGES ON DATABASE $DATABASE TO $USER;"
        
        # So you dont run into any access problems
        sudo -u $ADMIN psql -c "ALTER DATABASE $DATABASE OWNER TO $USER;"

        echo "Database '$DATABASE' and user '$USER' created successfully with all permissions granted."
    
    # if the database exist than we can drop it with the user  
    else
        
        sudo -u $ADMIN psql -c "DROP DATABASE $DATABASE"
        sudo -u $ADMIN psql -c "DROP USER $USER"

        echo "Database '$DATABASE' and user '$USER'  have been successfully deleted"
    fi


# MAC OS
# checks OS system
elif [[ "$OSTYPE" == "darwin"* ]]; then

    # Checks if the database already exists
    if [ -z "$EXISTING_DATABASE" ]; then

    # Activate Virtual Enviroment
        echo Activating virtual Enviroment 
        python3 -m venv .venv
        source .venv/bin/activate
        echo $VIRTUAL_ENV


        # Install Packages
        echo Installing External Packages
        pip3 install -r requirements.txt
        
        # Start a PostgreSQL service
        brew services start postgresql
    
        # create new database
        sudo -u $ADMIN createdb $DATABASE

        # Create the new user and grant permissions
        sudo -u $ADMIN psql -c "CREATE USER $USER WITH ENCRYPTED PASSWORD '$PASSWORD';"
        sudo -u $ADMIN psql -c "GRANT ALL PRIVILEGES ON DATABASE $DATABASE TO $USER;"
        
        # So you dont run into any access problems
        sudo -u $ADMIN psql -c "ALTER DATABASE $DATABASE OWNER TO $USER;"

        echo "Database '$DATABASE' and user '$USER' created successfully with all permissions granted."

    # if the database exists we drop it with the user
    else
        
        sudo -u $ADMIN psql -c "DROP DATABASE $DATABASE"
        sudo -u $ADMIN psql -c "DROP USER $USER"

        echo "Database '$DATABASE' and user '$USER'  have been successfully deleted"
    fi

# if the OS system doesn't match than you will have to create the database manually but it will still create the enviroment and install the required packages
else {

    # Activate Virtual Enviroment
        echo Activating virtual Enviroment 
        python3 -m venv .venv
        source .venv/bin/activate
        echo $VIRTUAL_ENV


        # Install Packages
        echo Installing External Packages
        pip3 install -r requirements.txt
    
    echo "Sorry your operating system isn't compatable please manually create the database using the following steps"
    echo " "
    echo "1. Ensure your postgres service is running"
    echo "2. Create the database with the command 'CREATE DATABASE benjamindavies_api;' "
    echo "3. Create the user with the command 'CREATE USER api_tester WITH PASSWORD recipe;'"
    echo "4. Move into the database with command '\c benjamindavies_api'"
    echo "5. Grant user permissions with command 'GRANT ALL PRIVILEGES ON DATABASE benjamindavies_api TO api_tester;'"
    echo "6. Grant permission for schema with command 'GRANT ALL ON SCHEMA public TO api_tester;'"
}
fi