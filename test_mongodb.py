import pymongo, certifi, os
ca = certifi.where()
url = os.getenv("MONGO_DB_URL")
client = pymongo.MongoClient(url, tlsCAFile=ca)
print(client.list_database_names())