import config
from boto3.session import Session

class s3connector(object):

    def __init__(self):
        _session = Session(config.s3_config['access_key'], 
                           config.s3_config['secret_key'], 
                           region_name=config.s3_config['region'])
        self.client = _session.client('s3')

    def upload(self, key, data):
        try:
            self.client.put_object(Bucket=config.s3_config['bucket'], 
                                   Key=key, Body=data)
            return True
        except Exception:
            return False
        
    def download(self, key, start = None, end = None):
        try:
            if start is not None:
                _response = self.client.get_object(Bucket=config.s3_config['bucket'], 
                                                   Key=key, Range="bytes=%d-%d" % (start, end))
            else:
                _response = self.client.get_object(Bucket=config.s3_config['bucket'], 
                                                   Key=key)
            return _response['Body'].read()
        except Exception:
            return None

    def delete(self, key):
        try:
            self.client.delete_object(Bucket=config.s3_config['bucket'], 
                                      Key=key)
            return True
        except Exception:
            return False

    def is_exist(self, key):
        pass
