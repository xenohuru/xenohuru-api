"""
Management command: init_encrypted_db

Converts an existing plain SQLite database to SQLCipher AES-256 encrypted format,
or creates a fresh encrypted database if none exists.

Usage:
    python manage.py init_encrypted_db

This is a ONE-TIME operation. After running it:
  - db.sqlite3 is encrypted with DB_ENCRYPTION_KEY
  - You can safely commit it to GitHub
  - Only the correct DB_ENCRYPTION_KEY can open it
"""

import os
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Convert plain SQLite database to SQLCipher AES-256 encrypted format'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        try:
            import sqlcipher3.dbapi2 as sqlcipher_db
        except ImportError:
            raise CommandError(
                "sqlcipher3 is not installed. Run: pip install sqlcipher3"
            )

        key = getattr(settings, 'DB_ENCRYPTION_KEY', None) or os.environ.get('DB_ENCRYPTION_KEY', '')
        if not key:
            raise CommandError(
                "DB_ENCRYPTION_KEY is not set in your .env or environment variables.\n"
                "Generate a strong key: python -c \"import secrets; print(secrets.token_hex(32))\""
            )

        db_path = Path(settings.DATABASES['default']['NAME'])
        backup_path = db_path.with_suffix('.plain.bak')
        encrypted_path = db_path.with_suffix('.encrypted.tmp')

        if not db_path.exists():
            self.stdout.write(self.style.WARNING(
                f"No database found at {db_path}. "
                "Run migrations first: python manage.py migrate"
            ))
            return

        # Check if already encrypted
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            conn.execute('SELECT count(*) FROM sqlite_master;').fetchone()
            conn.close()
            already_encrypted = False
        except Exception:
            already_encrypted = True

        if already_encrypted:
            self.stdout.write(self.style.SUCCESS(
                "Database is already encrypted with SQLCipher. Nothing to do."
            ))
            return

        if not options['force']:
            self.stdout.write(self.style.WARNING(
                f"\nThis will encrypt: {db_path}\n"
                f"A backup will be saved to: {backup_path}\n"
            ))
            confirm = input("Continue? [y/N] ").strip().lower()
            if confirm != 'y':
                self.stdout.write("Aborted.")
                return

        self.stdout.write("Creating backup...")
        shutil.copy2(str(db_path), str(backup_path))

        self.stdout.write("Encrypting database with AES-256 (SQLCipher)...")

        # Use SQLCipher's sqlcipher_export() to encrypt in-place
        plain_conn = None
        enc_conn = None
        try:
            import sqlite3 as plain_sqlite
            plain_conn = plain_sqlite.connect(str(db_path))

            # Attach an encrypted database and export everything into it
            plain_conn.execute(f"ATTACH DATABASE '{encrypted_path}' AS encrypted KEY '{key}';")
            plain_conn.execute("SELECT sqlcipher_export('encrypted');")
            plain_conn.execute("DETACH DATABASE encrypted;")
            plain_conn.close()
            plain_conn = None

            # Replace original with encrypted version
            db_path.unlink()
            encrypted_path.rename(db_path)

            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Database encrypted successfully!\n"
                f"   Encrypted: {db_path}\n"
                f"   Backup:    {backup_path}\n\n"
                f"You can now safely commit db.sqlite3 to GitHub.\n"
                f"Delete the backup when you're confident: rm {backup_path}"
            ))

        except Exception as exc:
            if plain_conn:
                plain_conn.close()
            if encrypted_path.exists():
                encrypted_path.unlink()
            raise CommandError(f"Encryption failed: {exc}\nOriginal database is unchanged.")
