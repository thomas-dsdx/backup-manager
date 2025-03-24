import logging as log
import os
import tarfile
import tempfile
from datetime import datetime, timedelta, timezone
from google.cloud import storage
from google.oauth2 import service_account

class BackupManager:

    RETENTION_DAYS = 14

    def __init__(self, bucket_name: str, credentials_file_path: str):
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file_path)
        
        self.client = storage.Client(credentials=credentials)
        self.bucket_name = bucket_name
        self.bucket = self.client.get_bucket(bucket_name)

    def __make_archive(self, folder_path: str) -> tempfile.NamedTemporaryFile:
        archive = tempfile.NamedTemporaryFile(delete=True, suffix='.tar.gz')
        log.info(f'creating archive {archive.name}')
        with tarfile.open(archive.name, 'w:gz') as tar:
            log.info(f'adding {folder_path} to archive')
            tar.add(
                folder_path,
                arcname=os.path.basename(folder_path),
                recursive=True
                )
        return archive
    
    def backup_folder(self, folder_path: str, backup_root: str) -> None:
        archive = self.__make_archive(folder_path)
        blob = self.bucket.blob(
            f'{backup_root}/{os.path.basename(folder_path)}.tar.gz'
            )
        log.info(f'uploading archive {archive.name} to {blob.name}')
        blob.upload_from_filename(archive.name)
        archive.close()
    
    def delete_old_backups(self) -> None:
        blobs = self.bucket.list_blobs()
        for blob in blobs:
            if blob.time_created < (\
                datetime.now(timezone.utc) - \
                timedelta(days=self.RETENTION_DAYS)):
                log.info(f'deleting {blob.name}')
                blob.delete()
