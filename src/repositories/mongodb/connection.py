import os
from mongoengine import connect


def init_mongo() -> None:
    """
    Initialize the default MongoEngine connection.
    """
    mongo_uri = os.getenv("MONGO_URI", "mongodb://root:root@mongodb:27017")
    db_name = os.getenv("MONGO_DB_NAME", "movieRental")

    connect(
        db=db_name,
        host=mongo_uri,
        alias="default",
    )
