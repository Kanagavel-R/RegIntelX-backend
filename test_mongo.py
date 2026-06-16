from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://db-user:DbUser%4012345@cluster0.7rw3yao.mongodb.net/?appName=Cluster0"
)

try:
    client.admin.command("ping")
    print("MongoDB Connected Successfully!")
except Exception as e:
    print(e)