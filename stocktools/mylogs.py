"""
日志文件配置文件 logfile.ini
日志器：default
"""
import logging.config
from os import path

log_file_path = path.join(path.dirname(path.abspath(__file__)), './logfile.ini')

logging.config.fileConfig(log_file_path)

logger = logging.getLogger("default")


