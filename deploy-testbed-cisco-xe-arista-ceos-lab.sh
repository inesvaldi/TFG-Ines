#!/bin/bash

echo 'Deploying containerlab topology with Cisco XE CSR1000v and Arista cEOS routers, two Arista cEOS switches, and with four hosts...'

sudo containerlab deploy --topo telemetry-testbed-cisco-xe-arista-ceos-lab.yaml

echo 'Done!'

echo ''
echo ''

echo 'Configuring client "pc11" container...'

sudo docker exec -it clab-telemetry-testbed-cisco-xe-arista-ceos-lab-pc11 ifconfig eth1 10.0.1.2 netmask 255.255.255.0
sudo docker exec -it clab-telemetry-testbed-cisco-xe-arista-ceos-lab-pc11 ip route add 10.0.2.0/24 via 10.0.1.1 dev eth1

echo 'Done!'

echo ''
echo ''

echo 'Configuring client "pc12" container...'

sudo docker exec -it clab-telemetry-testbed-cisco-xe-arista-ceos-lab-pc12 ifconfig eth1 10.0.1.3 netmask 255.255.255.0
sudo docker exec -it clab-telemetry-testbed-cisco-xe-arista-ceos-lab-pc12 ip route add 10.0.2.0/24 via 10.0.1.1 dev eth1

echo 'Done!'

echo ''
echo ''

echo 'Configuring client "pc21" container...'

sudo docker exec -it clab-telemetry-testbed-cisco-xe-arista-ceos-lab-pc21 ifconfig eth1 10.0.2.2 netmask 255.255.255.0
sudo docker exec -it clab-telemetry-testbed-cisco-xe-arista-ceos-lab-pc21 ip route add 10.0.1.0/24 via 10.0.2.1 dev eth1

echo 'Done!'

echo ''
echo ''

echo 'Configuring client "pc22" container...'

sudo docker exec -it clab-telemetry-testbed-cisco-xe-arista-ceos-lab-pc22 ifconfig eth1 10.0.2.3 netmask 255.255.255.0
sudo docker exec -it clab-telemetry-testbed-cisco-xe-arista-ceos-lab-pc22 ip route add 10.0.1.0/24 via 10.0.2.1 dev eth1

echo 'Done!'

echo ''
echo ''

echo 'Configuring self-signed cert for RESTCONF management on router "r2" container...'
sleep 2
sudo docker exec -it clab-telemetry-testbed-cisco-xe-arista-ceos-lab-r2 Cli -p 15 -c "security pki certificate generate self-signed restconf.crt key restconf.key generate rsa 2048 parameters common-name restconf"

echo 'Done!'

echo ''
echo ''

echo 'All done!'
