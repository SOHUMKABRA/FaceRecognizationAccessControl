import cv2
import numpy as np
import time
import requests
from loguru import logger
import os
from datetime import datetime, timedelta
from utils import get_door_cloud_token, control_door
from FaceDetector import FaceDetector

class FaceRecognitionSystem:

    def __init__(self, rtsp_url, door_cloud_url):
        self.rtsp_url = rtsp_url
        self.door_cloud_url = door_cloud_url
        self.cap = cv2.VideoCapture(rtsp_url)
        self.face_detector = FaceDetector()
        self.recognition_url = "http://192.168.1.195:8000/api/v1/recognition/recognize?limit=5&prediction_count=1&det_prob_threshold=0.5"
        self.access_token = None
        self.token_last_refresh = 0
        self.token_expiration = 3599

        self.door_open = False  # Flag variable to track door state
        self.last_door_open_time = None  # Time when the door was last opened
        self.u_d_map = {}
        self.log_details= {}

        self.frame_counter = 0
        self.skip_factor = 5

    def encode_frame(self, frame):
        try:

            # Prepare the frame for sending
            _, img_encoded = cv2.imencode('.jpg', frame)
            return img_encoded
        except Exception as e:
            logger.error(f"{e}")

    def recognise_faces(self, files):
        try:
            self.recognise_face_header = "a165d599-2cea-4519-8470-32148366d24e"
            header = {
                'x-api-key': self.recognise_face_header
            }
            response = requests.post(self.recognition_url, headers=header, files=files)

            if response.status_code == 200 or response.status_code == 400:
                data = response.json()
                return data

            else:
                raise Exception(f"[FACE RECOGNITION]:{response.json()}")

        except Exception as e:
            logger.error(f"[FACE RECOGNITION]:{e}")

    def judge_face_data(self,results,frame,time_string, current_time):
        try:
            self.similarity = 0
            logger.info(f"NO OF SUBJECTS DETECTED: {len(results)}")
            # dimensions = subjects[0].get('dimension')
            for result in results:
                dimension = result['box']
                subjects = result['subjects']
                self.x1 = dimension['x_min']
                self.x2 = dimension['x_max']
                self.y1 = dimension['y_min']
                self.y2 = dimension['y_max']
                for subject in subjects:
                    self.subject_name = subject['subject']
                    self.similarity = subject['similarity']

                if self.similarity > 0.95:

                    cv2.rectangle(frame, (self.x1, self.y1), (self.x2, self.y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{self.subject_name}:{self.similarity}", (self.x1, self.y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    cv2.putText(frame, f"{self.x1} x {self.y1}", (self.x2, self.y2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    # Get the current time
                    current_time = time.time()

                    # Check if the access token needs to be refreshed
                    if current_time - self.token_last_refresh >= self.token_expiration or access_token is None:
                        # Refresh the access token
                        access_token = get_door_cloud_token()

                        # Update the last refresh time
                        token_last_refresh = current_time

                    self.person_name = subjects[0]['subject']
                    # cheking for same person
                    if self.person_name in self.u_d_map is not None:
                        self.currtime = datetime.now()

                        if self.currtime >= self.u_d_map[self.person_name] + timedelta(seconds=5):
                            control_door(access_token)
                            self.u_d_map[self.person_name] = datetime.now()
                            logger.success("Open the Door ")
                        else:
                            logger.warning("Cannot open the door")
                    else:
                        control_door(access_token)
                        self.u_d_map[self.person_name] = datetime.now()
                        logger.info("Entering for first time")

                    # Create a folder for the person if it doesn't exist
                    self.folder_path = os.path.join(os.getcwd(), "dataset", self.person_name)
                    os.makedirs(self.folder_path, exist_ok=True)
                    self.subject_image_files = os.listdir(self.folder_path)
                    if len(self.subject_image_files) == 0:
                        # Save the image inside the person's folder
                        self.image_filename = f"{time_string}_{self.similarity}.jpeg"
                        self.save_path = os.path.join(self.folder_path, self.image_filename)
                        cv2.imwrite(self.save_path, frame)



                    elif len(self.subject_image_files) > 0:
                        # print(subject_image_files)
                        check_file_name = self.subject_image_files[-1]
                        check_date, check_time = check_file_name.split('.jpeg')[0].split('_')[:2]
                        date_time_str = check_date + '_' + check_time
                        # Convert the Str Datetime to Datetime Object:
                        file_dt = datetime.strptime(date_time_str, "%Y-%m-%d_%H-%M-%S")
                        # print("Date time now ",datetime.now())
                        time_diff = datetime.now() - file_dt

                        # print(time_diff)
                        if time_diff.seconds > 300:
                            # Wrtie a New File with New Datetime
                            # Save the image inside the person's folder
                            self.image_filename = f"{time_string}_{self.similarity}.jpeg"
                            self.save_path = os.path.join(self.folder_path, self.image_filename)
                            # Save the image inside the person's folder
                            self.folder_path = os.path.join(os.getcwd(), "dataset", self.person_name)
                            os.makedirs(self.folder_path, exist_ok=True)
                            cv2.imwrite(self.save_path, frame)
                            start_time = current_time
                        else:

                            existing_images = os.listdir(self.folder_path)
                            if len(existing_images) > 0:
                                existing_images.sort()
                                latest_image_path = os.path.join(self.folder_path, existing_images[-1])
                                os.remove(latest_image_path)
                            # Save the image inside the person's folder
                            self.image_filename = f"{time_string}_{self.similarity}.jpeg"
                            self.save_path = os.path.join(self.folder_path, self.image_filename)
                            cv2.imwrite(self.save_path, frame)
                    logger.info(f"{self.subject_name}:{self.similarity}")


                    if self.person_name not in self.log_details:
                        curr_time = datetime.now()
                        logger.debug("Face data: {person_name} - {similarity} ",person_name=self.person_name, similarity=self.similarity)
                        #with open('log.txt','a') as log_file:
                         #   log_file.write(f'Face data: {self.person_name} - {self.similarity}  - {curr_time}\n')


                        self.log_details[self.person_name] = datetime.now()
                    else:

                        if datetime.now() >= self.log_details[self.person_name] + timedelta(seconds=600):
                            # Log the face data after 10 minutes
                            curr_time = datetime.now()
                            logger.debug("Face data: {person_name} - {similarity} ", person_name=self.person_name, similarity=self.similarity)
                            # with open('log.txt', 'a') as log_file:
                            #     log_file.write(f'Face data: {self.person_name} - {self.similarity} - {curr_time} \n')


                            self.log_details[self.person_name] = datetime.now()



                elif (self.similarity < 0.95) and (self.similarity > 0.5):
                    # else:
                    subject = subjects[0].get('list')
                    cv2.rectangle(frame, (self.x1, self.y1), (self.x2, self.y2), (0, 0, 255), 2)
                    cv2.putText(frame, f"{self.subject_name}:{self.similarity}", (self.x1, self.y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,(0, 0, 255), 2)
                    # Get the person's name
                    self.person_name = subjects[0]['subject']

                    # Create a folder for the person if it doesn't exist
                    self.folder_path = os.path.join(os.getcwd(), "dataset", "unknown", self.person_name)
                    os.makedirs(self.folder_path, exist_ok=True)
                    self.subject_image_files = os.listdir(self.folder_path)

                    if (self.subject_image_files == []):
                        # Save the image inside the person's folder
                        self.image_filename = f"{time_string}_{self.similarity}.jpeg"
                        self.save_path = os.path.join(self.folder_path, self.image_filename)
                        cv2.imwrite(self.save_path, frame)

                    if len(self.subject_image_files) > 0:
                        # print(subject_image_files)
                        check_file_name = self.subject_image_files[0]
                        check_date, check_time = check_file_name.split('.jpeg')[0].split('_')[:2]
                        date_time_str = check_date + '_' + check_time
                        # Convert the Str Datetime to Datetime Object:
                        file_dt = datetime.strptime(date_time_str, "%Y-%m-%d_%H-%M-%S")

                        time_diff = datetime.now() - file_dt
                        # print(time_diff)
                        if time_diff.seconds > 600:
                            # Wrtie a New File with New Datetime
                            # Save the image inside the person's folder
                            self.image_filename = f"{time_string}_{self.similarity}.jpeg"
                            self.save_path = os.path.join(self.folder_path, self.image_filename)
                            # Save the image inside the person's folder
                            self.folder_path = os.path.join(os.getcwd(), "dataset", self.person_name)
                            os.makedirs(self.folder_path, exist_ok=True)
                            cv2.imwrite(self.save_path, frame)
                            start_time = current_time
                        else:

                            existing_images = os.listdir(self.folder_path)
                            if len(existing_images) > 0:
                                existing_images.sort()
                                latest_image_path = os.path.join(self.folder_path, existing_images[-1])
                                os.remove(latest_image_path)
                            # Save the image inside the person's folder
                            self.image_filename = f"{time_string}_{self.similarity}.jpeg"
                            self.save_path = os.path.join(self.folder_path, self.image_filename)
                            cv2.imwrite(self.save_path, frame)
                    logger.info(f"{self.subject_name}:{self.similarity}")
                else:
                    logger.warning(f"Recognition Similarity was very LOW: {self.similarity}")


        except Exception as e:
            logger.error(f"{e}")

    def run(self):
        try:
            logger.add("log_data.log", level="DEBUG", filter=lambda record: record["level"].name == "DEBUG")


            while True:

                ret, frame = self.cap.read()
                if frame is None:
                    logger.error("[CAP ERROR]: Failed to Read Frame from Camera")
                    break

                self.frame_counter += 1
                if self.frame_counter % self.skip_factor != 0:
                    continue

                frame = cv2.resize(frame, (750, 500), 0.0, 0.0, interpolation=cv2.INTER_CUBIC)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                img_encoded = self.encode_frame(frame)
                detect_state, face_data = self.face_detector.maininfer(frame)

                if np.any(detect_state > 0):
                    results = face_data
                    if results is not None and len(results) != 0:
                        current_time = time.time()
                        time_string = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(current_time))
                        files = {'file': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')}
                        data = self.recognise_faces(files)
                        results = data.get('result')
                        self.judge_face_data(results, frame, time_string, current_time)

                    else:
                        logger.warning("[NO FACE FOUND]")
                cv2.imshow("Camera Preview", frame)
                self.save_path = f"Live/live.jpeg"
                cv2.imwrite(self.save_path, frame)


                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            self.cap.release()
            cv2.destroyAllWindows()

        except Exception as e:
            logger.error(f"{e}")
