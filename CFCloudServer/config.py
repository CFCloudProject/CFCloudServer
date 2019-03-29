# server config
port = '6060'
one_day_in_seconds = 24 * 60 * 60

# s3 config
s3_config = { 
    'access_key': 'AKIAI3GZAZ77PXWO3HOQ', 
    'secret_key': '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', 
    'region': 'ap-southeast-1', 
    'bucket': '19cloud1' 
    }

# efs config
efs_root = ''
efs_file_root = efs_root + '/namespaces'

# mysql config
mysql_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'BID_db',
    'charset': 'utf8'
    }

# sqlite3 config
sqlite3_db_path = efs_root + '/cfcloud.db'
psi_db_path = efs_root + '/psi.db'

# psi config
psi_root = efs_root + '/psi'

# container config
container_max_size = 4 * 1024 * 1024

# cache config
container_cache_max_capacity = 50
metadata_cache_max_capacity = 400
psi_cache_max_capacity = 50
