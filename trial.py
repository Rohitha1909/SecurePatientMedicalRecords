import ssl


def get_database():
    from pymongo import MongoClient
    import pymongo

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    # CONNECTION_STRING = "mongodb+srv://Aronique:29094964@cluster0.hs3g1.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"



    # CONNECTION_STRING = "mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/myFirstDatabase"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    from pymongo import MongoClient
    import certifi

    CONNECTION_STRING = "mongodb+srv://nurse:nurse123@cluster0.hs3g1.mongodb.net/"
    client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())['hospital']


    print(client.list_collection_names())

    # Create the database for our example (we will use the same database throughout the tutorial


# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":
    # Get the database
    get_database()