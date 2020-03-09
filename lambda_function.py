import boto3
import os
from PIL import Image
import pathlib
from io import BytesIO

# configuration
thumbimagebucket = 'resizedimagebucket0099'
backupimagebucket = 'backupimagebucket0099'
mainimagebucket = 'myimagebucket0099'
client = boto3.client('s3')
s3 = boto3.resource('s3')

def delete_this_bucket(name):
    '''
        def     delete_this_bucket()
        param   bucket_name

        This function deletes all object at first by looping through.
        As it is required by AWS programmatic access cant delete the
        whole bucket at once.
    '''
    bucket = s3.Bucket(name)
    for key in bucket.objects.all():
        try:
            key.delete()
            bucket.delete()
        except Exception as e:
            print("SOMETHING IS BROKEN !!")

def create_this_bucket(name, location):
    '''
        def create_this_bucket()
        param bucket_name, bucket_location

        this function will create bucket from a given location and name
    '''
    try:
        s3.create_bucket(
            Bucket=name,
            CreateBucketConfiguration={
                'LocationConstraint': location
            }
        )
    except Exception as e:
        print(e)

def upload_test_images(name):
    '''
        def upload_test_images()
        param bucket_name

        this function responsible for uploading images in bucket
    '''
    for each in os.listdir('./testimage'):
        try:
            file = os.path.abspath(each)
            s3.Bucket(name).upload_file(file, each)
        except Exception as e:
            print(e)

def copy_to_other_bucket(src, des, key):
    try:
        copy_source = {
            'Bucket': src,
            'Key': key
        }
        bucket = s3.Bucket(des)
        bucket.copy(copy_source, key)
    except Exception as e:
        print(e)


def resize_image(src_bucket, des_bucket):
    size = 500, 500
    bucket = s3.Bucket(src_bucket)
    in_mem_file = BytesIO()
    client = boto3.client('s3')
    response = client.list_objects_v2(Bucket=src_bucket, Prefix='uploads/')
    
    for obj in response['Contents']:
        print(obj['Key'])
        file_byte_string = client.get_object(Bucket=src_bucket, Key=obj['Key'])
        try:
            im = Image.open(BytesIO(file_byte_string['Body'].read()))    
            im.thumbnail(size, Image.ANTIALIAS)
            
            # ISSUE : https://stackoverflow.com/questions/4228530/pil-thumbnail-is-rotating-my-image
            im.save(in_mem_file, format=im.format)
            in_mem_file.seek(0)
            
            response = client.put_object(
                Body=in_mem_file,
                Bucket=des_bucket,
                Key=obj['Key']
            )
        except Exception as e:
            print(e)
            pass

def lambda_handler(event, context):
    response = client.list_objects_v2(Bucket=mainimagebucket, Prefix='uploads/')

    for obj in response['Contents']:
        copy_to_other_bucket(mainimagebucket, backupimagebucket, obj['Key'])
    
    resize_image(mainimagebucket, thumbimagebucket)