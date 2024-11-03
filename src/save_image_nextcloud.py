import os
import requests
from datetime import datetime
import logging
import comfy.utils


from PIL import Image
import numpy as np
import piexif

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class SaveImageNextcloud:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename": ("STRING", {"default": "image.avif"})
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "save_to_nextcloud"
    CATEGORY = "api/image"
    OUTPUT_NODE = True

    def save_to_nextcloud(self, images, filename):
        logging.debug(f"CALL save_to_nextcloud")
        today_date = datetime.now().strftime("%Y%m%d")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # 환경 변수에서 인증 정보 가져오기
        username = os.environ.get("NEXTCLOUD_USERNAME")
        password = os.environ.get("NEXTCLOUD_PASSWORD")
        nextcloud_base_url = os.environ.get("NEXTCLOUD_URL")

        if not all([username, password, nextcloud_base_url]):
            logging.error("Nextcloud 인증 정보가 설정되지 않았습니다.")
            return {}

        # 현재 워크플로우 정보 가져오기

        workflow_data = comfy.manager.get_current_workspace()
        import json
        workflow_json = json.dumps(workflow_data)

        for idx, image in enumerate(images):
            # 이미지 처리
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8)).convert("RGB")  # AVIF는 RGB 포맷 사용

            # EXIF 데이터에 워크플로우 정보 포함
            exif_dict = {"0th": {}, "Exif": {}, "1st": {}, "thumbnail": None}
            exif_dict["Exif"][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(workflow_json, encoding="unicode")
            exif_bytes = piexif.dump(exif_dict)

            # 파일명 생성
            filename_with_time = f"{timestamp}_{idx}_{filename}"
            save_path = f"/tmp/{filename_with_time}"

            # EXIF 데이터를 포함하여 이미지 저장 (AVIF 포맷)
            img.save(save_path, "AVIF", exif=exif_bytes, quality=80)
            logging.debug(f"Image saved to {save_path}")

            # Nextcloud WebDAV 설정
            nextcloud_url = f"{nextcloud_base_url}/remote.php/dav/files/{username}/Photos/{today_date}/{filename_with_time}"
            nextcloud_folder_url = f"{nextcloud_base_url}/remote.php/dav/files/{username}/Photos/{today_date}/"

            # Nextcloud에 날짜 디렉토리 생성 요청
            logging.debug(f"Creating directory: {nextcloud_folder_url}")
            response = requests.request("MKCOL", nextcloud_folder_url, auth=(username, password))

            if response.status_code == 405:
                logging.debug(f"Directory {nextcloud_folder_url} already exists.")
            elif response.status_code == 201:
                logging.debug(f"Directory {nextcloud_folder_url} created successfully.")
            else:
                logging.debug(f"Failed to create directory. Status code: {response.status_code}")

            # 파일 업로드
            logging.debug(f"Uploading file to {nextcloud_url}")
            with open(save_path, "rb") as file:
                response = requests.put(nextcloud_url, auth=(username, password), data=file)
                if response.status_code in [201, 204]:
                    logging.debug(f"File {filename_with_time} uploaded successfully.")
                else:
                    logging.debug(f"Failed to upload {filename_with_time}. Status code: {response.status_code}")

        return {}

# 노드 등록
NODE_CLASS_MAPPINGS = {
    "SaveImageNextcloud": SaveImageNextcloud
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageNextcloud": "Save Image to Nextcloud"
}
