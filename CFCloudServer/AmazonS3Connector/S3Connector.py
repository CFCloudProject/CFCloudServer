import Config
from boto3.session import Session

class S3Connector(object):

    def __init__(self):
        _session = Session(Config.access_key, Config.secret_key, region_name=Config.region)
        self.client = _session.client('s3')

    def upload(self, key, data):
        try:
            self.client.put_object(Bucket=Config.bucket, Key=key, Body=data)
            return true
        except Exception:
            return false

    def download(self, key, start, end):
        try:
            _response = self.client.get_object(Bucket=Config.bucket, Key=key, Range="bytes=%d-%d" %(start,end))
            return _response['Body'].read()
        except Exception:
            return None

    def delete(self):
        pass

    def is_exist(self):
        pass