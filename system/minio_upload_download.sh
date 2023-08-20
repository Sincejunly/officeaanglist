#!/bin/bash

# MinIO Server configuration

MINIO_ENDPOINT="http://192.168.5.4:9000"
MINIO_ACCESS_KEY="homura"
MINIO_SECRET_KEY="aa159756"
BUCKET_NAME="gitlab-cache"

# Check for command line arguments
if [ $# -ne 2 ]; then
    echo "Usage: $0 <-up|-d> <path>"
    exit 1
fi

OPERATION="$1"
input_path="$2"

# Handle the upload operation
if [ "$OPERATION" == "-up" ]; then
    echo "Uploading..."

    # Get the directory name for creating compressed file
    DIRECTORY_NAME=$(basename "$input_path")
    COMPRESSED_FILE="$DIRECTORY_NAME.tar.gz"

    # Compress the directory
    #tar -czvf "$COMPRESSED_FILE" "$input_path"

    # Upload the compressed file to MinIO
    mc alias set myminio "$MINIO_ENDPOINT" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY"
    mc mb "myminio/$BUCKET_NAME"
    mc cp "$COMPRESSED_FILE" "myminio/$BUCKET_NAME/$COMPRESSED_FILE"
    #mc ls "$BUCKET_NAME"
    #mc rb "myminio/cache" --force

    echo "Upload completed."
fi

# Handle the download operation
if [ "$OPERATION" == "-d" ]; then
    echo "Downloading..."

    # Check if the compressed file exists
    FILE_NAME=$(basename "$input_path")
    if ! mc ls "$BUCKET_NAME/$FILE_NAME" &>/dev/null; then
        echo "File $FILE_NAME not found on MinIO. Exiting."
        exit 1
    fi

    # Download the compressed file from MinIO
    mc alias set myminio "$MINIO_ENDPOINT" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY"
    mc cp "$BUCKET_NAME/$FILE_NAME" "$FILE_NAME"

    # Extract the compressed file
    tar -xzvf "$FILE_NAME"

    echo "Download and extraction completed."
fi

