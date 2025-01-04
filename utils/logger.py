import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Suppress logs from the httpx package
logging.getLogger('httpx').setLevel(logging.CRITICAL)

# Suppress scheduler logs
logging.getLogger('apscheduler.scheduler').setLevel(logging.WARNING)
