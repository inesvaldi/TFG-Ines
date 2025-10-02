# Containerlab testbeds for studying and analyzing RESTCONF and CORECONF model-driven network management protocols.

This [Containerlab](https://containerlab.dev/) scenario allows users to study and analyze with network management mechanisms using the RESTCONF and CORECONF protocols and YANG data modeling language.

![Containerlab testbed scenario](img/topology.png)

## Deploying, playing with, and destroying the network topology

### Building custom Docker image for Linux clients

To build the custom Docker image for client end-hosts (i.e., `pc11`, `pc12`, `pc21`, and `pc22`), follow the steps below:
```
$ cd docker/
$ sudo docker build -t giros-dit/clab-telemetry-testbed-ubuntu:latest .
```

### Deploying the network topology

Before starting the Containerlab scenario it is necessary to import the [Arista cEOS](https://containerlab.dev/manual/kinds/ceos/) docker image. Specifically, the scenario uses one of the latest available Arista cEOS versions `cEOS-lab-4.34.3M`. Download it first from the [Arista software section](https://www.arista.com/en/support/software-download) (it is the 64-bit version).

The command to import the image is:
```bash
$ docker import cEOS64-lab-4.34.3M.tar ceos:4.34.3M
```

To deploy the network topology, simply run the deploy shell script:
```
$ ./deploy-testbed-arista-ceos-lab.sh
```

### Interacting with containers

For **Arista cEOS routers/switches**, via SSH to open the CLI (password is `admin`):
```
$ ssh admin@clab-telemetry-testbed-arista-ceos-lab-r1 # For r1 router
```

or with `docker exec` to open the interactive CLI:
```
$ sudo docker exec -it clab-telemetry-testbed-arista-ceos-lab-r1 Cli # For r1 router
```

For **Linux containers (clients)**, with `docker exec` to open an interactive shell:
```
$ sudo docker exec -it clab-telemetry-testbed-arista-ceos-lab-pc11 bash # For pc11 client container
```

### Destroying the network topology

To destroy the network topology, simply run the destroy shell script:
```
$ ./destroy-testbed-arista-ceos-lab.sh
```