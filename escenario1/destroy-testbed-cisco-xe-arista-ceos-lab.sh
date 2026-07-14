#!/bin/bash

echo 'Destroying containerlab topology with Cisco XE CSR1000v and Arista cEOS routers, two Arista cEOS switches, and with four hosts...'

sudo containerlab destroy --topo telemetry-testbed-cisco-xe-arista-ceos-lab.yaml

sudo rm -Rf clab-telemetry-testbed-cisco-xe-arista-ceos-lab/

echo 'Done!'

echo ''
echo ''

echo 'All done!'
