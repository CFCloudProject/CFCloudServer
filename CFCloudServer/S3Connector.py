import Global
from boto3.session import Session

class S3Connector(object):

    def __init__(self):
        _session = Session(Global.access_key, Global.secret_key, region_name=Global.region)
        self.client = _session.client('s3')

    def upload(self, key, data):
        try:
            self.client.put_object(Bucket=Global.bucket, Key=key, Body=data)
            return True
        except Exception:
            return False

    def download(self, key, start = None, end = None):
        try:
            if start is not None:
                _response = self.client.get_object(Bucket=Global.bucket, Key=key, Range="bytes=%d-%d" %(start,end))
            else:
                _response = self.client.get_object(Bucket=Global.bucket, Key=key)
            return _response['Body'].read()
        except Exception:
            return None

    def delete(self, key):
        try:
            self.client.delete_object(Bucket=Global.bucket, Key=key)
            return True
        except Exception:
            return False

    def is_exist(self, key):
        pass