# This tool is a graphic interface for regularly scanning a network and monitoring services and hosts.

To install, cd to the installer directory and run the `install.sh` script in the installer directory

    ./install.sh

If the installer worked correctly, you should be able to navigate to http://127.0.0.1:5000/active

*Note:* 

- *If you want the web application to run constantly, run the installer in a screen or tmux session*
- *nmap scans are currently configured for only a few ports, in order to scan two /16 networks in under a day. For smaller networks, you can change the nmap script to monitor other ports.*
- *If you want to start the nmap scans immediately, run `python3 nmap/nmap_recon.py`*
- *If you need to restart the web app, cd to the `App` directory, and `export FLASK_APP=connect.py` then run `flask run`*
