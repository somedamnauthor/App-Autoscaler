Getting started:
================

Installed podman - 
had to do some gymnastics to get this working on Ubuntu 20.04

Installed buildah

Creating the webapp container:
==============================

Created container from alpine linux - container=$(buildah from alpine)

Installed python3 - 
buildah run $container -- apk update
buildah run $container -- apk add python3

Installed pip3 - 
buildah run $container -- apk add py3-pip

Installed flask-restful using pip3 -
buildah run $container -- pip3 install flask-restful

Installed flask-limiter using pip3 - 
buildah run $container -- pip3 install --ignore-installed flask-limiter

edited .py file objst.py (File provided) - hardcoded datapath

Created app folder and copied in the app file and data. DATA SHOULD BE MOUNTED ideally
buildah copy $container cco1/webapp.py /root/webApp/objst.py
buildah copy $container cco1/data /root/webApp/data

committed container - 
buildah commit $container webappcontainer2

created podman network named 'mynetwork' - 
podman network create --driver=bridge mynetwork

ran container using - 
podman run -d --rm --name mycontainer --net mynetwork webappcontainer2



Setting up loadbalancer:
========================

pulled haproxy image - 
https://github.com/haproxytech/haproxy-docker-alpine

Created new directory 'haproxy' to store haproxy config file

Created new file in new directory for the config file - haconfig.cfg (File provided)
 
ran haproxy container using - 
podman run -d --restart always --name lbcontainer -p 8080:8080 -p 9999:9999 -p 8888:8888 -v /home/srishankar/Documents/cco1/haproxyFiles/haproxy:/etc/haproxy --net mynetwork d9d8ef41d986cd
(the last string is the image ID for the pulled haproxy image)

If config file is changed, kill container using - 
podman kill -s HUP lbcontainer