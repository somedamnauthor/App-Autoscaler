from random import randrange
from locust import HttpUser, task

class User(HttpUser):

    @task
    def getData(self):
        self.client.get("/")

    @task
    def putData(self):
        objIdString = "/objs/" + str(randrange(10000))
        self.client.put(objIdString, {"content":"swarm attack2!"})
        # with self.client.put(objIdString, {"content":"swarm attack2!"}, catch_response=True) as response:
        #     print("Response:",response)