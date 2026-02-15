import os
from pocketbase import PocketBase

# Connect and authenticate with PocketBase
try:
    db = PocketBase(os.environ['POCKETBASE_URL'])
    db.admins.auth_with_password(
        os.environ['ADMIN_EMAIL'], os.environ['ADMIN_PASSWORD'])
except Exception as e:
    raise Exception("Failed to connect to PocketBase with error: " + str(e))


class BaseModel():
    def __init__(self):
        if not hasattr(self.__class__, "collection_name"):
            raise Exception("Missing collection_name in model class")

        if not hasattr(self.__class__, "schema"):
            raise Exception("Missing schema in model class")

        self.collection_name = self.__class__.collection_name
        self.schema = self.__class__.schema

    def create(self):
        data = {
            field["name"]: getattr(self, field["name"])
            for field in self.schema
            if hasattr(self, field["name"])
        }
        return db.collection(self.collection_name).create(data)

    @classmethod
    def create_collection(cls):
        try:
            db.collections.get_one(cls.collection_name)
            return
        except Exception:
            pass

        try:
            db.collections.create({
                "name": cls.collection_name,
                "type": "base",
                "schema": cls.schema
            })
        except Exception as e:
            raise Exception("Failed to create collection " +
                            cls.collection_name + ": " + str(e))
