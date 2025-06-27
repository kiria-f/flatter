import os
from pathlib import Path

from loguru import logger


def main():
    log_file_path = Path(os.environ['APP_ROOT_DIR']) / 'app.log'
    if not log_file_path.exists():
        log_file_path.touch()
    logger.remove()
    logger.add(log_file_path, rotation='1 MB')
    logger.info('This is a test log message.')


if __name__ == '__main__':
    main()
    print("ok")
    input('Press Enter to exit...')
