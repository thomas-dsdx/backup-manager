import os
from datetime import datetime
import logging as log
from pathlib import Path
from manager import BackupManager

log.basicConfig(
    level=log.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)

def main():
    
    bucket_name = os.getenv('BUCKET_NAME')
    credentials_file_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    backup_mount = Path(os.getenv('BACKUP_MOUNT'))
    
    log.info(f'initializing backup manager')
    manager = BackupManager(bucket_name, credentials_file_path)
    folders_to_backup = [str(d) for d in backup_mount.iterdir() if d.is_dir()]
    backup_root = datetime.now().strftime('%Y-%m-%d')
    for folder in folders_to_backup:
        if not os.path.isdir(folder):
            log.error(f'{folder} is not a directory')
            continue
        log.info(f'backing up {folder}')
        manager.backup_folder(folder, backup_root)
    
    log.info(f'deleting old backups')
    manager.delete_old_backups()

if __name__ == '__main__':
    main()