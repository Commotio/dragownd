#!/bin/bash

# Check for package prerequisites 

# Python3
which python3 > /dev/null 2>&1
if [ $? -ne 0 ]; then
    # Not installed
    echo "Error: Python3 not installed. Install Python3 and rerun install.sh"
    echo "Exiting..."
    exit 1
fi

# MySQL
which mysql > /dev/null 2>&1
if [ $? -ne 0 ]; then
    # Not installed
    echo "Error: MySQL not installed. Install MySQL and rerun install.sh"
    echo "Exiting..."
    exit 1
fi

# Nmap
which nmap > /dev/null 2>&1
if [ $? -ne 0 ]; then
    # Not installed
    echo "Error: Nmap not installed. Install Nmap and rerun install.sh"
    echo "Exiting..."
    exit 1
fi


# Install Python3 Dependencies
echo 'Installing Python requirements...'
sudo apt update
sudo apt install default-libmysqlclient-dev
pip install -r requirements.txt
pip3 install -r requirements.txt
echo 'Python requirements successfully installed!'


# Import SQL objects
# Get root SQL password
echo 'Installing MySQL schema, tables, views, and users...'
read -sp 'MySQL root password: ' mysql_root_pass
sed -i "s/{{ password }}/$mysql_root_pass/" install.mysql_users
mysql -uroot -p'' -e "alter user 'root'@'localhost' identified by $mysql_root_pass" 

# Restart mysql to make sure it's running
systemctl restart mysql

# Upgrade mysql
mysql_upgrade -u root -p$mysql_root_pass --force
# Import DB, tables, views, procedures, and users
mysql -uroot -p$mysql_root_pass < install.mysql_users
mysql -uroot -p$mysql_root_pass < install.mysql

echo 'MySQL schema, tables, views, and users successfully installed!'

# Install Nmap recon
echo 'Installing Nmap recon scanning...'
read -p "Absolute path to the dragownd repo (include the dragownd directory? Ex. '/home/dragownd': " path
read -p "Please enter the desired network range/ranges in CIDR format, separated by commas - Ex. '127.0.0.1/16,10.0.0.1/16': " ranges
echo -e ${ranges/,/$'\n'} > ../nmap/ranges.txt

sed -i "s|{{ path }}|$path|" $path/nmap/nmap_recon.py
sed -i "s/{{ password }}/$mysql_root_pass/" $path/nmap/nmap_recon.py
sed -i "s/{{ password }}/$mysql_root_pass/" $path/App/connect.py

mkdir $path/archives

echo 'Installing Nmap recon cron...'
echo "0 1 * * * cd $path && python3 $path/nmap_recon.py > $path/crontab.log" > /etc/cron.d/dragownd
echo 'Nmap recon cron successfully installed!'

echo 'Nmap recon scanning successfully installed!'

# Install Flask
echo 'Installing Dragownd Flask App...'
cd $path/App

# Start Flask
export FLASK_APP=$path/App/connect.py
flask run
