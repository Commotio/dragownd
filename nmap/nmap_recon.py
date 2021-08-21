import xmltodict
from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime
import socket, struct
import os, sys
import subprocess

# # GLOBAL VARIABLES # # # # # # # # # # # # # # # # #
DIRECTORY = r'{{ path }}/nmap' #change
path = DIRECTORY + r'/nmap.sh'

DB_USER = "dragownd"
DB_PASSWD = "{{ password }}" #change
DB_HOST = "{{ hostvars['db'].ansible_host }}"
DB_NAME = "dragownd"
# # # # # # # # # # # # # # # # # # # # # # # # # # #


def ip2long(ip):
    """
    Convert an IP string to long
    """
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]

def extractDataFromXML(xmlFile):

    try:
        with open(DIRECTORY + '/' + xmlFile, 'r') as file:
            data_dict = xmltodict.parse(file.read())

        if 'host' not in data_dict['nmaprun'].keys():
            # No hosts found, skip
            return None

        # Tue Feb 23 17:55:54 2021
        xml_timestamp = datetime.strptime(data_dict['nmaprun']['@startstr'], "%c")

        # Iterate through data and pull out necessary data
        results = []
        for host in data_dict['nmaprun']['host']:

            # A host may contain multiple ports if multiples ports in the scan were found open
            # If so, these host['ports']['port'] needs to be iterated through

            if isinstance(host['ports']['port'], list):
                # Multiple open ports
                for port in host['ports']['port']:

                    # Make sure port is open, not open|filtered
                    if port['state']['@state'] != "open":
                        # If not open, skip result
                        break                    

                    # Try to pull out data, substitute null if value isn't present
                    d = {
                        "ip": ip2long(host['address']['@addr']) if "address" in host.keys() else None,
                        "ip_str": host['address']['@addr'] if "address" in host.keys() else None,
                        "port": port['@portid'] if "ports" in host.keys() else None,
                        "hostname": host['hostnames']['hostname']['@name'] if "hostnames" in host.keys() and host[
                            'hostnames'] is not None else None,
                        "transport": port['@protocol'] if "ports" in host.keys() else None,
                        "product": None,  # This may eventually be added to the nmap scans
                        "version": None,  # This may eventually be added to the nmap scans
                        "os": None,  # This may eventually be added to the nmap scans
                        "date": xml_timestamp.strftime("%Y-%m-%d"),
                        "active": True
                        }

                    # Store dictionary in results list
                    results.append(d)

            # Just one open port
            else:

                # Make sure port is open, not open|filtered
                if host['ports']['port']['state']['@state'] != "open":
                    # If not open, skip result
                    break

                d = {
                    "ip": ip2long(host['address']['@addr']) if "address" in host.keys() else None,
                    "ip_str": host['address']['@addr'] if "address" in host.keys() else None,
                    "port": host['ports']['port']['@portid'] if "ports" in host.keys() else None,
                    "hostname": host['hostnames']['hostname']['@name'] if "hostnames" in host.keys() and host['hostnames'] is not None else None,
                    "transport": host['ports']['port']['@protocol'] if "ports" in host.keys() else None,
                    "product": None,  # This may eventually be added to the nmap scans
                    "version": None,  # This may eventually be added to the nmap scans
                    "os": None,  # This may eventually be added to the nmap scans
                    "date": xml_timestamp.strftime("%Y-%m-%d"),
                    "active": True
                }

                # Store dictionary in results list
                results.append(d)

        if results:
            # Create Pandas DataFrame with results
            columns = list(d.keys())
            return pd.DataFrame(results, columns=list(set(columns)))

    except Exception as e:
        print(DIRECTORY + '/' + xmlFile)
        raise e

def main():

    # Start nmap scan
    nmap_scan = subprocess.Popen(['sudo', 'bash', path])
    nmap_scan.wait()

    if nmap_scan.returncode != 0:
        # Error
        print("There was an error running the NMAP scans. Exiting.")
        sys.exit(1)

    # Create connection to database
    engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                           .format(user=DB_USER, pw=DB_PASSWD,
                                   host=DB_HOST, db=DB_NAME))

    # Parse XML results
    for filename in os.listdir(DIRECTORY):
        if filename.endswith(".xml"):

            # Pull out data from XML into dataframe
            df = extractDataFromXML(filename)

            # Store results in host_LastImport and call Merge_LastImport stored procedure
            # df is None is no hosts were found in scan
            if df is not None:
                df.to_sql('host_LastImport', con=engine, if_exists='append', index=False)

    # Call Merge_LastImport stored procedure
    engine.execute('call `%s`.Merge_LastImport;' % DB_NAME)

    # Archive scan results
    #subprocess.call("./archive.sh")


if __name__ == "__main__":
    main()
