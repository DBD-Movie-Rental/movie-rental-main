import os
from mongoengine import connect


def init_mongo() -> None:
    """
    Initialize the default MongoEngine connection.
    """
    # Base values from env (compose sets these for in-container runs)
    mongo_uri = os.getenv("MONGO_URI", "mongodb://root:root@mongodb:27017")
    db_name = os.getenv("MONGO_DB_NAME", "movieRental")
    auth_source_env = os.getenv("MONGO_AUTH_SOURCE")

    # If credentials are present in the URI and no authSource provided, default to admin
    # This matches how the root user is created by mongo: it lives in the 'admin' database
    if ("@" in mongo_uri) and ("authSource=" not in mongo_uri):
        if auth_source_env:
            sep = "&" if "?" in mongo_uri else "?"
            mongo_uri = f"{mongo_uri}{sep}authSource={auth_source_env}"
        else:
            sep = "&" if "?" in mongo_uri else "?"
            mongo_uri = f"{mongo_uri}{sep}authSource=admin"

    # When running the API outside Docker (e.g., local dev) the hostname 'mongodb'
    # doesn't resolve. If RUNNING_IN_DOCKER is not set, prefer localhost.
    running_in_docker = os.getenv("RUNNING_IN_DOCKER") == "true"
    if not running_in_docker and "mongodb://" in mongo_uri and "@mongodb:" in mongo_uri:
        # Map to the published localhost port 27017
        mongo_uri = mongo_uri.replace("@mongodb:", "@localhost:")

    connect(
        db=db_name,
        host=mongo_uri,
        alias="default",
    )
