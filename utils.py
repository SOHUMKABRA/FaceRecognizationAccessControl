from loguru import logger
import requests

import json

def get_door_cloud_token():


        url = "https://api.doorcloud.com/token"
        payload = 'client_id=DoorCloudWebApp&grant_type=password&username=dummy.in&password=dummy'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'ARRAffinity=176da18497bc474167a1a6cec921cf64cc23be973f0f93dd5e4c2bd8b5c0478c; ARRAffinitySameSite=176da18497bc474167a1a6cec921cf64cc23be973f0f93dd5e4c2bd8b5c0478c'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        access_token=response.text


        #print(response.status_code)
        #get_door_cloud_token(access_token)
        return access_token
        pass





def control_door(access_token):
    try:
        data = json.loads(access_token)
        token = data['access_token']

        url = "https://api.doorcloud.com/api/OutputManagement/ChangeStatus"

        payload = json.dumps({
            "id": "a0a0df4d-81cf-4630-ac03-b012004a0c71",
            "statusId": 4
        })
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',

        }

        response = requests.request("POST", url, headers=headers, data=payload)
        logger.info(f"{response}")

        #(response.text)
        (response.status_code)
    except Exception as e:
        logger.error(f"{e}")
    pass

