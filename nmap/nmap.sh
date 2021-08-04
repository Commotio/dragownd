#!/bin/bash
#Requires ranges.txt (newline delimited list of ranges)
#Outputs standard nmap --max-parallelism 100 --min-hostgroup 100 files as well as webips.txt and IoT.txt
# webips.txt: list of IPs with web ports open in format <ip>:<port>
# merged.txt: list of webips.txt merged with IoT.txt (For importing to SQL DB)
#Add/remove services as needed

touch webips.txt

#var=$(date +"%FORMAT_STRING")
#now=$(date +"%m_%d_%Y")
#printf "%s\n" $now
today=$(date +"%Y-%m-%d")
filename="nmap_"$today".txt"

#web scans for IPs
nmap -T4 --max-parallelism 100 --min-hostgroup 100 -sS --open --randomize-hosts --script=http-title.nse --script-args=http.useragent="Mozilla/5.0; Windows NT 6.1; WOW64; Trident/7.0; rv:11.0; like Gecko" -g 53 -p80,81,443,8080,8081,8443,8880 -iL ranges.txt -oA Web
awk '/Status\: Up/{print $2":81"}' Web.gnmap >> webips.txt

#IOT
nmap -T4 --max-parallelism 100 --min-hostgroup 100 -sS --open --randomize-hosts -g 53 -p21,22,23,2323,53,990,623,135,139,137,445, 5800,5900,5901,3389,1723,5631,1494,5902,10000,1433,1521,1526,3306,523,5432,27017,27018,27019,9200,9300,5601,5044,25,587,110,143,5060,5061,2222,2223,52869,37215,37777,8090 -iL ranges.txt -oA IoT
awk '/Status\: Up/{print $2":81"}' IoT.gnmap >> IoT.txt

#Backnet
nmap -T4 --max-parallelism 100 --min-hostgroup 100 --open --randomize-hosts -g 53 -sU -p47808 -iL ranges.txt -oA BACnet
awk '/Status\: Up/{print $2":81"}' BACnet.gnmap >> IoT.txt

#merge
cat webips.txt >> merged.txt
echo -ne "\n" >> merged.txt
cat IoT.txt >> merged.txt

mv merged.txt $filename
