#!/bin/bash

echo 'Destroying containerlab topology with two Arista cEOS routers, two Arista cEOS switches, and with four hosts...'

sudo containerlab destroy --topo telemetry-testbed-arista-ceos-lab.yaml

sudo rm .telemetry-testbed-arista-ceos-lab.yaml.bak
sudo rm -Rf clab-telemetry-testbed-arista-ceos-lab/

echo 'Done!'

echo ''
echo ''

echo 'All done!'
