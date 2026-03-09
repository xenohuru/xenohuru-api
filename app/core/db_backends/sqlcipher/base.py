"""
SQLCipher-backed Django database backend.

Drop-in replacement for django.db.backends.sqlite3 that uses SQLCipher
(AES-256-CBC) to encrypt the database file at rest.

Requirements:
    pip install sqlcipher3

Usage in settings.py:
    DATABASES = {
        'default': {
            'ENGINE': 'app.core.db_backends.sqlcipher',
            'NAME': BASE_DIR / 'chui.db',
        }
    }
    DB_ENCRYPTION_KEY = config('DB_ENCRYPTION_KEY')
"""

import os

from django.conf import settings
from django.db.backends.sqlite3 import base as sqlite_base


class DatabaseWrapper(sqlite_base.DatabaseWrapper):
    """
    SQLite backend that opens the database with SQLCipher AES-256 encryption.
    The encryption key is read from settings.DB_ENCRYPTION_KEY (or the env var
    DB_ENCRYPTION_KEY directly) and applied as PRAGMA key immediately after
    the connection is created — before any other operation.
    """

    def get_new_connection(self, conn_params):
        try:
            import sqlcipher3.dbapi2 as sqlcipher_db
        except ImportError as exc:
            raise ImportError(
                "SQLCipher backend requires 'sqlcipher3'. "
                "Run: pip install sqlcipher3"
            ) from exc

        conn = sqlcipher_db.connect(**conn_params)

        key = getattr(settings, 'DB_ENCRYPTION_KEY', None) or os.environ.get('DB_ENCRYPTION_KEY', '')
        if not key:
            raise RuntimeError(
                "DB_ENCRYPTION_KEY is not set. "
                "Set it in your .env file or environment variables."
            )

        # Key MUST be the very first PRAGMA — before any read or write
        conn.execute(f'PRAGMA key="{key}";')

        # Verify the key is correct (raises OperationalError if wrong key)
        try:
            conn.execute('SELECT count(*) FROM sqlite_master;').fetchone()
        except Exception as exc:
            conn.close()
            raise RuntimeError(
                "DB_ENCRYPTION_KEY is incorrect — cannot open the database."
            ) from exc

        # SQLCipher performance tuning (all must come after PRAGMA key)
        conn.execute('PRAGMA cipher_page_size=4096;')          # 4KB pages (default 1KB)
        conn.execute('PRAGMA kdf_iter=256000;')                 # PBKDF2 iterations
        conn.execute('PRAGMA cipher_hmac_algorithm=HMAC_SHA512;')
        conn.execute('PRAGMA cipher_kdf_algorithm=PBKDF2_HMAC_SHA512;')

        # SQLite WAL + performance (max concurrent reads)
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.execute('PRAGMA synchronous=NORMAL;')
        conn.execute('PRAGMA cache_size=-32000;')               # 32MB page cache
        conn.execute('PRAGMA temp_store=MEMORY;')
        conn.execute('PRAGMA mmap_size=536870912;')             # 512MB mmap
        conn.execute('PRAGMA foreign_keys=ON;')
        conn.execute('PRAGMA wal_autocheckpoint=1000;')

        return conn
