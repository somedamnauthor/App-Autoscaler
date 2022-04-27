Getting started:
================

1) podman required
2) buildah required



Creating the webapp container:
==============================

1) Go to the 'application' directory and execute the commands given in buildCommands.txt to build the podman image named 'webappcontainer2'

2) Run container using - 

podman run -d --rm --name mycontainer --net mynetwork webappcontainer2



Setting up loadbalancer:
========================

1) Go to the haproxyFiles directory 

2) Build image named 'my-haproxy' using the given Dockerfile in the haproxyFiles directory - 

podman build -t my-haproxy .

Run haproxy container using the command below. Note that the haproxy directory (inside the haproxyFiles directory) is volume mounted. These paths will have to be changed to match the current directory structure -
 
podman run -d --restart always --name lbcontainer -p 8080:8080 -p 9999:9999 -p 8888:8888 -v /home/srishankar/Documents/cco1/haproxyFiles/haproxy:/etc/haproxy --net mynetwork my-haproxy
(the last string is the image ID for the my-haproxy image)

#If config file is changed, kill container using - 
#podman kill -s HUP lbcontainer
