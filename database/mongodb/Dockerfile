FROM mongo:7

# Copy the keyfile into the image
COPY replica.key /etc/mongo/replica.key

# Force the correct permissions and ownership inside the image
# 999 is the default 'mongodb' user ID in the official image
RUN chmod 400 /etc/mongo/replica.key && \
    chown 999:999 /etc/mongo/replica.key

# Start MongoDB with the replica set and keyfile arguments
CMD ["mongod", "--replSet", "rs0", "--bind_ip_all", "--port", "27017", "--keyFile", "/etc/mongo/replica.key"]
