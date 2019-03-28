import s3connector
import cache
import user_session
import config

_s3_connector = s3connector.s3connector()
_metadata_cache = cache.cache(config.metadata_cache_max_capacity, 'metadata')
_container_cache = cache.cache(config.container_cache_max_capacity, 'container')
_user_session = user_session.user_session(config.sqlite3_db_path)
