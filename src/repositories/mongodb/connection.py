from mongoengine import connect

# Initialize MongoDB connection
def init_mongo():
    # Connect to the MongoDB database
    connect(
        db="movie_rental_mongo",
        host="mongodb://localhost:27017",
        alias="mongodb_connection", 
    )
