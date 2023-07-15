from FaceRecognitionSystem import FaceRecognitionSystem
from loguru import logger


if __name__ == '__main__':
    try:
        rtsp_url = "rtsp://admin:Iam_1234@192.168.1.180:554/"
        #rtsp_url = 0
        door_cloud_url = "https://api.doorcloud.com/api/OutputManagement/ChangeStatus"

        system = FaceRecognitionSystem(rtsp_url, door_cloud_url)
        system.run()

    except Exception as e:
        logger.error(f"[INITIALISATION FAILED]: {e}")
