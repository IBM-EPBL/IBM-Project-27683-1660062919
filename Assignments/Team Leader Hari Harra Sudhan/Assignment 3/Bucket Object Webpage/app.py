from flask import Flask, redirect, url_for, render_template, request
import ibm_boto3
from ibm_botocore.client import Config, ClientError

COS_ENDPOINT = "https://s3.au-syd.cloud-object-storage.appdomain.cloud"
COS_API_KEY_ID = "56n8SgPcBBJ37R7IFnUNgiylptI2xgi3S2L-ETT5lnhx"
COS_INSTANCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/f013f33e120446db92c1a7285a31c323:37e64cf0-5312-4e91-ab50-811807779f3b::"

# Create resource https://s3.ap.cloud-object-storage.appdomain.cloud
cos = ibm_boto3.resource("s3",
                         ibm_api_key_id=COS_API_KEY_ID,
                         ibm_service_instance_id=COS_INSTANCE_CRN,
                         config=Config(signature_version="oauth"),
                         endpoint_url=COS_ENDPOINT
                         )

app = Flask(__name__)


def get_item(bucket_name, item_name):
    print("Retrieving item from bucket: {0}, key: {1}".format(bucket_name, item_name))
    try:
        file = cos.Object(bucket_name, item_name).get()

        print("File Contents: {0}".format(file["Body"].read()))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve file contents: {0}".format(e))


def get_bucket_contents(bucket_name):
    print("Retrieving bucket contents from: {0}".format(bucket_name))
    try:
        files = cos.Bucket(bucket_name).objects.all()
        files_names = []
        for file in files:
            files_names.append(file.key)
            print("Item: {0} ({1} bytes).".format(file.key, file.size))
        return files_names
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve bucket contents: {0}".format(e))


def delete_item(bucket_name, object_name):
    try:
        cos.Object(bucket_name, object_name).delete()
        print("Item: {0} deleted!\n".format(object_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to delete object: {0}".format(e))


def multi_part_upload(bucket_name, item_name, file_path):
    try:
        print("Starting file transfer for {0} to bucket: {1}\n".format(item_name, bucket_name))
        # set 5 MB chunks
        part_size = 1024 * 1024 * 5

        # set threadhold to 15 MB
        file_threshold = 1024 * 1024 * 15

        # set the transfer threshold and chunk size
        transfer_config = ibm_boto3.s3.transfer.TransferConfig(
            multipart_threshold=file_threshold,
            multipart_chunksize=part_size
        )

        # the upload_fileobj method will automatically execute a multi-part upload
        # in 5 MB chunks for all files over 15 MB
        with open(file_path, "rb") as file_data:
            cos.Object(bucket_name, item_name).upload_fileobj(
                Fileobj=file_data,
                Config=transfer_config
            )

        print("Transfer for {0} Complete!\n".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to complete multi-part upload: {0}".format(e))


@app.route('/')
def index():
    file1 = get_bucket_contents('hari-harra-sudhan-assignment3')
    return render_template('index.html', files=file1)


@app.route('/deletefile', methods=['GET', 'POST'])
def deletefile():
    if request.method == 'POST':
        bucket = request.form['bucket']
        name_file = request.form['filename']

        delete_item(bucket, name_file)
        return 'file deleted successfully'

    if request.method == 'GET':
        return render_template('delete.html')


@app.route('/uploader', methods=['GET', 'POST'])

def upload():
    if request.method == 'POST':
        bucket = request.form['bucket']
        name_file = request.form['filename']
        f = request.files['file']
        multi_part_upload(bucket, name_file, f.filename)
        return 'file uploaded successfully <a href="/">GO to Home</a>'

    if request.method == 'GET':
        return render_template('upload.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8089, debug=True)