import logging
import boto3
from botocore.exceptions import ClientError


class S3services:
    def create_bucket(bucket_name, region=None):
        # Create bucket
        try:
            if region is None:
                s3_client = boto3.client('s3')
                s3_client.create_bucket(Bucket='fandoo-static')
            else:
                s3_client = boto3.client('s3', region_name='ap-south-1')
                location = {'LocationConstraint': region}
                s3_client.create_bucket(Bucket='fandoo-static',
                                        CreateBucketConfiguration=location)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    """List Existing Buckets
    List all the existing buckets for the AWS account."""

    # Retrieve the list of existing buckets
    def list_buckets(self):
        s3 = boto3.client('s3')
        response = s3.list_buckets()

        # Output the bucket names
        print('Existing buckets:')
        for bucket in response['Buckets']:
            print(f'  {bucket["Name"]}')


