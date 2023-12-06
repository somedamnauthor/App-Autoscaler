Getting started:
================

This tool is an autoscaler that deploys your application as a Podman container and automatically scales up and scales down multiple instances of it based on incoming load. The instances are loadbalanced through a self-managed load-balancer.

1) podman required

2) buildah required



Creating the webapp container:
==============================

1) Go to the 'application' directory and execute the commands given in buildCommands.txt to build the podman image named 'webappcontainer2'

2) Create a podman network named 'mynetwork' -

 ```
podman network create --driver=bridge mynetwork
```

2) Run c
   
```
podman run -d --rm --name mycontainer --net mynetwork webappcontainer2
```


Setting up loadbalancer:
========================

1) Go to the haproxyFiles directory 

2) Build image named 'my-haproxy' using the given Dockerfile in the haproxyFiles directory - 

```
podman build -t my-haproxy .
```

3) Run haproxy container using the command below. Note that the haproxy directory (inside the haproxyFiles directory) is volume mounted. 
These paths will have to be changed to match the current directory structure. Specifically change /home/srishankar/Documents/cco1/haproxyFiles/haproxy to the haproxy folder containing the config file

```
podman run -d --restart always --name lbcontainer -p 8080:8080 -p 9999:9999 -p 8888:8888 -v /home/srishankar/Documents/cco1/haproxyFiles/haproxy:/etc/haproxy --net mynetwork my-haproxy
```
(the last string is the image ID for the my-haproxy image)



Execute Scalingcontroller:
==========================

1) Go to the scalingController directory

2) Execute the scaling controller using - 

```
python3 autoscaler.py
```


Execute requestGenerator:
=========================

1) Go to the requestGenerator directory

2) Execute the 'pattern.sh' shell script - which starts and stops locust jobs in a specific pattern



Observation:
============

Observe the scalingController scaling containers up and down from the stats page of HAProxy - http://localhost:9999/stats
