"""
Main process to detect humans and trigger the motion detection
"""
import sys
import logging
from video import wand_finder

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    stream=sys.stdout,
)

class WandReader:
    def __init__(self):
        logger.info("starting main process init")
        #TODO: I need to eventually enable this self.homekit_api = homebridge.HomebridgeAPI()
    def start(self) -> None:
        with wand_finder.Detector(camera_index=0) as detector:
            while True:
                logger.info("starting detection loop")
                position = detector.check_for_wand_spot()
                if position is None:
                    logger.info("no reflector found")
                else:
                    x, y = position
                    logger.info(f"Reflector found at ({x}, {y})")

if __name__ == "__main__":
    wr = WandReader()
    wr.start()
