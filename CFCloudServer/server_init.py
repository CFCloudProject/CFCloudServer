import S3Connector
import cache
import user_session
import block_index
import psi
import config
import utils
import os
import uuid

_s3_connector = S3Connector.s3connector()
_metadata_cache = cache.cache(config.metadata_cache_max_capacity, 'metadata')
_container_cache = cache.cache(config.container_cache_max_capacity, 'container')
_psi_cache = cache.cache(config.psi_cache_max_capacity, 'psinode')
_hash_cache = cache.hashcache()
_user_session = user_session.user_session(config.sqlite3_db_path)
_block_index = block_index.block_index()
_psi = psi.psi(config.psi_db_path)
_log = open(config.efs_root + '/ot.log', 'w')
_log.close()

def init():
    if not os.path.exists(config.efs_file_root):
        os.mkdir(config.efs_file_root)

    if not os.path.exists(config.psi_root):
        os.mkdir(config.psi_root)

    # create the first psinode and container
    psid = str(uuid.uuid1())
    container_id = utils.get_new_container_id()
    pnode = _psi_cache.get_usable_node(psid)
    pnode.acquire_lock()
    pnode.create({ 
        'type': 'a', 
        'id': psid, 
        'paths': [config.efs_file_root], 
        'container_ids': [container_id] 
        })
    pnode.release_lock()
    cnode = _container_cache.get_usable_node(container_id)
    cnode.acquire_lock()
    cnode.create(container_id)
    cnode.release_lock()
