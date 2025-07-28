from azure.storage.blob import BlobServiceClient
import os

container_string = "your container key string"
container_name = "raw"

def uploadToBlob(file_path, file_name):
    blob_service_clinet = BlobServiceClient.from_connection_string(container_string)
    blob_client = blob_service_clinet.get_blob_client(container=container_name, blob=file_name)

    with open(file_path,"rb") as data:
        blob_client.upload_blob(data)
    print("Uploaded {file_name}")

uploadToBlob(r"D:\codes\Data Engineer\Pokemon\data\pokemon.csv", "pokesmon.csv")