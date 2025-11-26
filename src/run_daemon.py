import schedule
import time
import logging
import sys
import os

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def job():
    logger.info("Starting scheduled job...")
    try:
        main()
        logger.info("Job completed successfully.")
    except Exception as e:
        logger.error(f"Job failed: {e}")

if __name__ == "__main__":
    logger.info("TrendMonitor Daemon Started")
    logger.info("Schedule: Every 1 hour")
    
    # Run immediately on startup
    job()
    
    # Schedule every hour
    schedule.every(1).hours.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
