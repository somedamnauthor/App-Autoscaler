import csv
import requests

import time

import os



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

    if numContainersToDelete == 0:
        return

    filepath = '../haproxyFiles/haproxy/haproxy.cfg'

    newFileList = []
    skippedContainers = []
    
    #Create a new file without the required number of backends, so that the containers are removed from the haproxy config
    numLinesSkipped = 0
    for line in reversed(list(open(filepath))):

        if numLinesSkipped < numContainersToDelete and line.rstrip()!='':
            
            numLinesSkipped += 1

            left = 'server  '
            right = ' mycontainer'
            skippedContainers.append(line[line.index(left)+len(left):line.index(right)])
            continue

        else:

            newFileList.append(line.rstrip())
    
    newFileList.reverse()

    while newFileList[-1]=='':
        newFileList.pop(-1)

    #Write the contents onto file
    with open(filepath, 'w') as f:
        for item in newFileList:
            f.write("%s\n" % item)

    #Kill HAProxy container, which is set to restart with the new config
    os.system('podman kill -s HUP lbcontainer')

    #Kill the containers
    for app in skippedContainers:
        if app[-1]!='1':
            containerName = 'mycontainer'+app[-1]
            # deleteCommand = 'podman rm -f '+containerName
            deleteCommand = 'podman kill '+containerName
            print(deleteCommand)
            os.system(deleteCommand)



def monitor():

    CSV_URL = "http://localhost:9999/stats;csv"

    numRequests = 0

    justScaled = False
    firstTryAction = True

    timeForCleanup = 0

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
        
        initialRequests = numRequests
        newRequests = int(dataList[-1][7]) - numRequests
        numRequests = int(dataList[-1][7])

        if justScaled == True:
            print("\nLetting requests update\n")
            justScaled = False
            continue
        
        if initialRequests!=0 and newRequests>0:

            if firstTryAction == True:
                print("\nDelaying action to next try\n")
                firstTryAction = False
                continue

            if numContainers*20 <= newRequests:
                numToSpawn = int(newRequests/20) - numContainers + 1

                print("\nNew requests:", newRequests, "\nCurrent containers: ", numContainers, "\nNumber of containers to spawn: ",numToSpawn)
                # startTime = time.time()
                spawnContainers(numContainers, numToSpawn)
                # endTime = time.time()
                # print("Time taken to spawn containers:",endTime - startTime)
                justScaled = True
                firstTryAction = True
                time.sleep(1)

            else:
                numToDelete = numContainers - int(newRequests/20) - 1
                print("\nNew requests:", newRequests, "\nCurrent containers: ", numContainers, "\nNumber of containers to delete: ",numToDelete)
                if numToDelete > 0:
                    # removeContainers(numToDelete)
                    # startTime = time.time()
                    removeContainers(1)
                    # endTime = time.time()
                    # print("Time taken to remove 1 container:",endTime-startTime)
                    justScaled = True
                    firstTryAction = True
                    time.sleep(1)
                else:    
                    time.sleep(1)

        else:
            print("No new requests")
            timeForCleanup += 1
            if timeForCleanup == 20:
                janitor()
                timeForCleanup = 0
            time.sleep(1)



def janitor():

    print("\nCommencing podman clean-up\n")

    containers = list(os.popen('podman ps --format {{.Names}}').read().split('\n'))
    containers = [container for container in containers if container!='mycontainer' and container!='' and container!='lbcontainer']
    
    for container in containers:
        deleteCommand = 'podman kill ' + container
        print(deleteCommand)
        os.system(deleteCommand)

    print("\nCompleted podman clean-up")
    
    print("\nCleaning HAProxy")
    removeContainers(len(containers))
    os.system('cp ../haproxyFiles/haproxy/backup.cfg ../haproxyFiles/haproxy/haproxy.cfg')
    os.system('podman kill -s HUP lbcontainer')
    print("\nCompleted HaProxy cleanup\n")


# removeContainers(3)
# spawnContainers(1, 4)


def experiments():

    spawn = []
    remove = []

    for i in range(1,11):

        start = time.time()
        spawnContainers(1,i)
        end = time.time()
        spawn.append(end-start)
        # print("Time taken for spawn:",end-start)

        start = time.time()
        removeContainers(i)
        end = time.time()
        remove.append(end-start)
        # print("Time taken for remove:",end-start)


    print("Spawn times:",spawn)
    print("Remove times:",remove)


monitor()

# experiments()