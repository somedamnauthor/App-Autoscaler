# import urllib.request
# contents = urllib.request.urlopen("http://localhost:9999/stats;csv").read()
# print(contents)

import csv
import requests

import time

# from podman import PodmanClient
import os

def monitor():

    CSV_URL = "http://localhost:9999/stats;csv"

    numRequests = 0

    while True:
        
        with requests.Session() as s:
            download = s.get(CSV_URL)

        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        dataList = list(cr)

        #The first value in the list tells us what type of resource is being monitored by haproxy
        #Thus the number of entries in the list of rows that have the value 'app' in the 0th index tells us how many containers we have running
        #The above value is 1 more than the actual number of containers, so 1 is subtracted
        numContainers = [row[0] for row in dataList].count('app') - 1

        #dataList[-1] corresponds to the 'backend' row in the stats page. This row has the stats for all the backends put together
        #The [7]th index contains the total number of requests that have been made up until that point
        #Thus the 'change' in the number of requests between now and the previous instant is calculated
        newRequests = int(dataList[-1][7]) - numRequests
        numRequests = int(dataList[-1][7])
        
        print(newRequests)
        
        time.sleep(1)


def spawnContainers(numContainersPresent, numContainersToSpawn):

    for i in range(numContainersToSpawn):

        currentContainer = numContainersPresent + 1 + i
        containerName = "mycontainer" + str(currentContainer)
        appName = "app"+str(currentContainer)

        print("Creating container with name:",containerName)
        createContainerCommand = "podman run -d --rm --name " + containerName + " --net mynetwork webappcontainer2"
        os.system(createContainerCommand)

        #Add container as backend to loadbalancer
        print("Adding",containerName,"to HAProxy backend")

        cfgFileObject = open('../haproxyFiles/haproxy/haproxy.cfg', 'a')
        line = "\n    server  "+appName+" "+containerName+":5000 check"
        print(line)
        cfgFileObject.write(line)
        cfgFileObject.close()

        #Restart HAProxy container
        os.system("podman kill -s HUP lbcontainer")


def removeContainers(numContainersToDelete):
    
    # for line in reversed(list(open('../haproxyFiles/haproxy/haproxy.cfg'))):
    #     print(line.rstrip())

    with 



# monitor()

# spawnContainers(1, 2)
removeContainers(4,2)