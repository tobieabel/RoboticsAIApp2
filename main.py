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

from flask import Flask, request, render_template
from google.cloud import storage

app = Flask(__name__)

# Configure this environment variable via app.yaml
#CLOUD_STORAGE_BUCKET = os.environ['roboticsaiapp_upload']
CLOUD_STORAGE_BUCKET = 'roboticsaiapp_upload2'


@app.route('/')
def index():
    return """
<form method="POST" action="/upload" enctype="multipart/form-data">
    <label for="jpg">Choose JPG file</label><br>
    <input type="file" id="jpg" name="file"> <br>
    <label for="jpg">Choose XML file</label><br>
    <input type="file" id="xml" name="xml"> <br>
    <input type="submit">
</form>
"""


@app.route('/upload', methods=['POST'])
def upload():
    """Process the uploaded file and upload it to Google Cloud Storage."""
    jpg_uploaded_file = request.files.get('file')
    xml_uploaded_file = request.files.get('xml')
    if (not jpg_uploaded_file) and (not xml_uploaded_file):
        return 'One of both files not uploaded.', 400

    if __name__ == '__main__':
    # Create a Cloud Storage client.
        gcs = storage.Client.from_service_account_json('roboticsaiapp2Key.json')


    # Or Explicitly use service account credentials by specifying the private key
    # file.
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
    #need to access files in GCP buckets, and save new ones to bucket
    result = synthetic.show_image(uploaded_file, uploaded_xml)
    return result



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
