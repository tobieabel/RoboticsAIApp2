# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_flex_storage_app]
import logging
import os
import synthetic
import requests
import socket

from flask import Flask, request, render_template
from google.cloud import storage

app = Flask(__name__)

# Configure this environment variable via app.yaml
#CLOUD_STORAGE_BUCKET = os.environ['roboticsaiapp_upload']
CLOUD_STORAGE_BUCKET = 'roboticsaiapp_upload2'


@app.route('/')
def index():
    return """
    <form method="POST" action="/prediction" enctype="multipart/form-data">
    <label for="jpg">Choose JPG file</label><br>
    <input type="file" id="jpg" name="file"> <br>
    <label for="jpg">Choose XML file</label><br>
    <input type="file" id="xml" name="xml"> <br>
    <input type="submit">
    </form>
"""

@app.route('/prediction', methods=['POST'])
def predict():#use this function to get the files uploaded by user, and send to cloud function using post in 'requests' module
    url = 'https://us-central1-roboticsaiobejctdetection.cloudfunctions.net/object_detection'
    jpg_uploaded_file = request.files.get('file')
    file = {'file': jpg_uploaded_file}
    prediction = requests.post(url,files = file)#this send the file to the cloud function endpoint
    return """<p>{}</p>""".format(prediction.content)

@app.route('/upload', methods=['POST'])
def upload():
    """Process the uploaded file and upload it to Google Cloud Storage."""
    jpg_uploaded_file = request.files.get('file')
    xml_uploaded_file = request.files.get('xml')
    if (not jpg_uploaded_file) and (not xml_uploaded_file):
        return 'One or both files not uploaded.', 400

    if __name__ == '__main__':
        # Explicitly use service account credentials by specifying the private key
        # file.
        gcs = storage.Client.from_service_account_json('roboticsaiapp2Key.json')



    # Create a Cloud Storage client.
    else:
        gcs = storage.Client()

    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)

    # Create a new blob and upload the file's content. blob refers to the thing you are uploading
    blob1 = bucket.blob("images/" + jpg_uploaded_file.filename)#you need to add the sub-directory of the bucket to the name of the blob - this is because the folder structure in GCP is not really a folder, just an object with a prefix
    blob2 = bucket.blob("labels/" + xml_uploaded_file.filename)

    blob1.upload_from_string(
        jpg_uploaded_file.read(),
        content_type=jpg_uploaded_file.content_type
    )
    blob2.upload_from_string(
        xml_uploaded_file.read(),
        content_type=xml_uploaded_file.content_type
    )

    # The public URL can be used to directly access the uploaded file via HTTP.
    #want to return new page which displays the url, and a button to run Synthetic images.py
    return render_template ('Synthetic.html', file = blob1.public_url, xml = blob2.public_url)

@app.route('/synthetic', methods = ['POST'])
def synth():
    uploaded_file = request.form["uploaded_file"]
    uploaded_xml = request.form["uploaded_xml"]
    #call show_image function to create new images and pass back the files for saving to cloud
    result = synthetic.show_image(uploaded_file, uploaded_xml)
    if __name__ == '__main__':
    # Create a Cloud Storage client.
        gcs = storage.Client.from_service_account_json('roboticsaiapp2Key.json')


    # Or Explicitly use service account credentials by specifying the private key
    # file.
    else:
        gcs = storage.Client()

    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    blob3 = bucket.blob("images/" + result[0])#is the blob just the filepath?
    blob3.upload_from_filename(result[0])#have to upload_from_filename not string or file as i only returned the filename string
    blob4 = bucket.blob("labels/" + result[1])
    blob4.upload_from_filename(result[1])
    blob5 = bucket.blob("images/" + result[2])
    blob5.upload_from_filename(result[2])

    os.remove(result[0])#remove the locally created jpg once uploaded
    os.remove(result[1])#and xml file
    os.remove(result[2])#and blur jpg
    #now return a fresh page with the below references, and an option to perform object detection on the new synthetic image
    return"""
    <h1>New jpg and xml files have been created. They have been stored on Google Cloud and can be accessed here...</h1>
    <p><a href="{}">Synthetic jpg</a></p>
    <p><a href="{}">Synthetic xml</a></p>
    <p><a href="{}">blur jpg</a></p>
    """.format(blob3.public_url, blob4.public_url, blob5.public_url)

@app.route('/connect')
def connect():#create a socket and start listening on port 443 for incoming messages - move this to html page
    s=socket.socket()
    s.bind(('',443))
    s.listen(5)
    while True:#need to think if this should be continous loop
        c, address = s.accept()
        if c:
            c.send("thanks for connecting")#should you test for c first, and only if true then send and return
            return """
            <h1>Establishing Connection...</h1>
            """#need to return a message to the pi, which then starts sending jpgs to a url which is referenced in my html ,src. element
        else:
            continue



@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_flex_storage_app]
