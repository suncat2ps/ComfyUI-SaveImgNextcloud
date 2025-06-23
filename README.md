# ComfyUI Save Image Nextcloud Plugin

This repository provides the `SaveImageNextcloud` node for ComfyUI. It uploads generated images to a Nextcloud server, stores them as AVIF or WebP, and can optionally create thumbnails and workflow JSON files.

## Installation

1. Install the required packages.
   ```bash
   pip install -r requirements.txt
   ```
2. Copy or symlink this plugin into ComfyUI's `custom_nodes` folder.
3. Create a `.env` file with your Nextcloud credentials:
   ```text
   NEXTCLOUD_USERNAME=<Nextcloud username>
   NEXTCLOUD_PASSWORD=<Nextcloud password>
   NEXTCLOUD_URL=<Nextcloud base URL>
   ```

## Node Options

* **images** – tensors representing the images to upload
* **filename** – base file name; the extension is added according to the selected format
* **format** – choose between `avif` and `webp`
* **c_quality** – compression quality (0–100)
* **enc_speed** – AVIF encoding speed (0–10)
* **create_thumbnail** – whether to generate a thumbnail
* **thumbnail_size** – size of the thumbnail’s longest side
* **thumbnail_quality** – quality for the WebP thumbnail
* **save_workflow_json** – whether to save workflow JSON metadata

When the node runs, it saves images to a temporary directory, optionally writes a thumbnail and workflow JSON, uploads the files to `Photos/<date>/` on the Nextcloud server, and removes the temporary files afterwards.

If the required environment variables are missing, the node raises `"Nextcloud 인증 정보가 설정되지 않았습니다."` as shown in the initialization code【F:src/save_image_nextcloud.py†L21-L28】.

## License

This project is licensed under the MIT License.

---

# ComfyUI Save Image Nextcloud 플러그인

이 저장소는 ComfyUI에서 생성한 이미지를 Nextcloud 서버로 업로드하는 `SaveImageNextcloud` 노드를 제공합니다. 이미지 파일을 AVIF 또는 WebP 형식으로 저장하며 필요에 따라 썸네일과 워크플로우 JSON 파일을 생성할 수 있습니다.

## 설치 방법

1. 필요한 패키지를 설치합니다.
   ```bash
   pip install -r requirements.txt
   ```
2. 플러그인을 ComfyUI의 `custom_nodes` 폴더에 복사하거나 심볼릭 링크를 만듭니다.
3. Nextcloud 인증 정보를 포함한 `.env` 파일을 작성합니다.
   ```text
   NEXTCLOUD_USERNAME=<Nextcloud 사용자 이름>
   NEXTCLOUD_PASSWORD=<Nextcloud 비밀번호>
   NEXTCLOUD_URL=<Nextcloud 인스턴스 기본 URL>
   ```

## 노드 사용 옵션

* **images**: 업로드할 이미지 텐서를 전달합니다.
* **filename**: 저장할 기본 파일 이름이며, 확장자는 선택한 형식에 따라 추가됩니다.
* **format**: `avif` 또는 `webp` 중에서 선택합니다.
* **c_quality**: 0~100 사이의 압축 품질 값입니다.
* **enc_speed**: AVIF 인코딩 속도를 0~10 사이로 지정합니다.
* **create_thumbnail**: 썸네일을 생성할지 여부입니다.
* **thumbnail_size**: 썸네일의 가장 긴 변의 길이입니다.
* **thumbnail_quality**: 썸네일 WebP 저장 시 품질입니다.
* **save_workflow_json**: 워크플로우 JSON 메타데이터를 저장할지 여부입니다.

노드가 실행되면 이미지가 임시 디렉터리에 저장되고, 필요하면 썸네일과 워크플로우 JSON이 생성되며, 파일이 Nextcloud 서버의 `Photos/<date>/` 경로에 업로드된 후 임시 파일이 삭제됩니다.

환경 변수가 설정되어 있지 않으면 초기화 단계에서 `"Nextcloud 인증 정보가 설정되지 않았습니다."` 오류가 발생합니다【F:src/save_image_nextcloud.py†L21-L28】.

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
