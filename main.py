from FaceRecognitionSystem import FaceRecognitionSystem
from loguru import logger


if __name__ == '__main__':
    try:
        #rtsp_url = "rtsp:///"
        door_cloud_url = "https://"

        system = FaceRecognitionSystem(rtsp_url, door_cloud_url)
        system.run()

    except Exception as e:
        logger.error(f"[INITIALISATION FAILED]: {e}")
