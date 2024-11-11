import os
import requests
from datetime import datetime
import logging
from PIL import Image
import numpy as np
import json
from comfy.cli_args import args
from dotenv import load_dotenv
import pillow_avif

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class SaveImageNextcloud:
    def __init__(self):
        # 환경 변수에서 인증 정보 가져오기
        self.username = os.getenv("NEXTCLOUD_USERNAME")
        self.password = os.getenv("NEXTCLOUD_PASSWORD")
        self.nextcloud_base_url = os.getenv("NEXTCLOUD_URL")

        if not all([self.username, self.password, self.nextcloud_base_url]):
            raise ValueError("Nextcloud 인증 정보가 설정되지 않았습니다.")

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename": ("STRING", {"default": "image.avif"}),
                "c_quality": ("INT", {"default": 75, "min": 0, "max": 100, "step": 1}),
                "enc_speed": ("INT", {"default": 6, "min": 0, "max": 10, "step": 1}),
                "create_thumbnail": ("BOOLEAN", {"default": True}),
                "thumbnail_size": ("INT", {"default": 250, "min": 50, "max": 500, "step": 10}),
                "thumbnail_quality": ("INT", {"default": 30, "min": 10, "max": 100, "step": 5}),
                "save_workflow_json": ("BOOLEAN", {"default": False})
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"}
        }

    RETURN_TYPES = ()
    FUNCTION = "save_to_nextcloud"
    CATEGORY = "api/image"
    OUTPUT_NODE = True

    def save_to_nextcloud(self, images, filename, c_quality=75, enc_speed=6, prompt=None, extra_pnginfo=None, thumbnail_size=100, thumbnail_quality=30, create_thumbnail=True, save_workflow_json=True):
        logging.debug(f"CALL save_to_nextcloud")
        today_date = datetime.now().strftime("%Y%m%d")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # 각 이미지를 반복하여 처리
        for idx, image in enumerate(images):
            try:
                # 이미지 처리 및 파일명 생성
                img = self._process_image(image)
                filename_with_time = f"{timestamp}_{idx}_{filename}"
                save_path = f"/tmp/{filename_with_time}"

                img_exif = img.getexif()

                if not args.disable_metadata:
                    if prompt is not None:
                        prompt_text = "".join(json.dumps(prompt))
                        img_exif[0x010f] = "Prompt: " + prompt_text
                    if extra_pnginfo is not None:
                        workflow_metadata = str()
                        for x in extra_pnginfo:
                            workflow_metadata += "".join(json.dumps(extra_pnginfo[x]))
                        img_exif[0x010e] = "Workflow: " + workflow_metadata

                # 이미지 저장 (AVIF 포맷)
                img.save(save_path, "AVIF", quality=c_quality, speed=enc_speed, exif=img_exif)
                logging.debug(f"Image saved to {save_path}")

                # 썸네일 생성 및 WEBP로 저장
                if create_thumbnail:
                    thumbnail_path = f"/tmp/{timestamp}_{idx}_{filename}_thumbnail.webp"
                    img.thumbnail((thumbnail_size, thumbnail_size), Image.LANCZOS)  # 썸네일 크기 줄이기, 비율 유지
                    img.save(thumbnail_path, "WEBP", quality=thumbnail_quality, exif=img_exif)  # 썸네일을 WebP로 저장하며 품질 줄이기
                    logging.debug(f"Thumbnail saved to {thumbnail_path}")
                    self._upload_to_nextcloud(today_date, f"{timestamp}_{idx}_{filename}_thumbnail.webp",
                                              thumbnail_path)

                # 워크플로우를 JSON 파일로 저장
                if save_workflow_json and extra_pnginfo is not None:
                    workflow_save_path = f"/tmp/{filename_with_time}.json"
                    with open(workflow_save_path, 'w') as json_file:
                        workflow_metadata = str()
                        for x in extra_pnginfo:
                            workflow_metadata += "".join(json.dumps(extra_pnginfo[x]))
                        json_file.write(workflow_metadata)
                    logging.debug(f"Workflow JSON saved to {workflow_save_path}")
                    self._upload_to_nextcloud(today_date, f"{filename_with_time}.json", workflow_save_path)

                # Nextcloud에 업로드
                self._upload_to_nextcloud(today_date, filename_with_time, save_path)

            finally:
                # 임시 파일 제거
                if os.path.exists(save_path):
                    os.remove(save_path)
                if save_workflow_json and extra_pnginfo is not None and os.path.exists(workflow_save_path):
                    os.remove(workflow_save_path)
                if create_thumbnail and os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)

        return {}

    # 이미지를 RGB 형식으로 처리하는 함수
    def _process_image(self, image):
        i = 255. * image.cpu().numpy()
        return Image.fromarray(np.clip(i, 0, 255).astype(np.uint8)).convert("RGB")

    # Nextcloud에 파일을 업로드하는 함수
    def _upload_to_nextcloud(self, date, filename, file_path):
        # Nextcloud WebDAV URL 설정
        nextcloud_url = f"{self.nextcloud_base_url}/remote.php/dav/files/{self.username}/Photos/{date}/{filename}"
        nextcloud_folder_url = f"{self.nextcloud_base_url}/remote.php/dav/files/{self.username}/Photos/{date}/"

        # Nextcloud에 날짜 디렉토리 생성 요청
        logging.debug(f"Creating directory: {nextcloud_folder_url}")
        response = requests.request("MKCOL", nextcloud_folder_url, auth=(self.username, self.password))

        # 디렉토리 생성 결과 처리
        if response.status_code not in [201, 405]:
            logging.error(f"Failed to create directory. Status code: {response.status_code}")
            raise Exception(f"Failed to create directory {nextcloud_folder_url}")

        # 파일 업로드
        logging.debug(f"Uploading file to {nextcloud_url}")
        with open(file_path, "rb") as file:
            response = requests.put(nextcloud_url, auth=(self.username, self.password), data=file)
            if response.status_code not in [201, 204]:
                logging.error(f"Failed to upload {filename}. Status code: {response.status_code}")
                raise Exception(f"Failed to upload file {filename}")

# 노드 등록
NODE_CLASS_MAPPINGS = {
    "SaveImageNextcloud": SaveImageNextcloud
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageNextcloud": "Save Image to Nextcloud"
}

# .env 파일 예시
# NEXTCLOUD_USERNAME=<Nextcloud 사용자 이름>
# NEXTCLOUD_PASSWORD=<Nextcloud 비밀번호>
# NEXTCLOUD_URL=<Nextcloud 인스턴스의 기본 URL (예: https://nextcloud.example.com)>
