import boto3
import os
from PIL import Image
import pathlib
from io import BytesIO

s3 = boto3.resource('s3')

def delete_this_bucket(name):
    bucket = s3.Bucket(name)
    for key in bucket.objects.all():
        try:
            key.delete()
            bucket.delete()
        except Exception as e:
            print("SOMETHING IS BROKEN !!")

def create_this_bucket(name, location):
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
        bucket.copy(f'upload/{copy_source}', f'upload/{key}')
    except Exception as e:
        print(e)

def resize_image(name):
    size = 500, 500
    bucket = s3.Bucket(name)

    for obj in bucket.objects.all():
        ext = pathlib.Path(obj.key).suffix.split('.')[1]
        im = Image.open(obj.key)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save('resized_' + obj.key)
        im.show()