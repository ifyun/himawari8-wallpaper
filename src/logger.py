import logging
from logging.handlers import RotatingFileHandler

log = logging.getLogger()
log.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

file_handler = RotatingFileHandler('./himawari8.log', 'a', 10240, 2, 'utf-8')
file_handler.setLevel(logging.INFO)

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
log.addHandler(console_handler)
log.addHandler(file_handler)
