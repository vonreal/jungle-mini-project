import os
import uuid
from PIL import Image, ImageOps

UPLOAD_FOLDER = 'static/uploads'

# 이미지 검증
def is_valid_image(file):
    try:
        with Image.open(file) as img:
            img.verify()
            return True
    except (IOError, SyntaxError):
        return False

def save_image(requestFiles, type="feed"):
    if 'image' not in requestFiles or requestFiles['image'].filename == '':
        raise ValueError()
    
    file = requestFiles['image']

    if not is_valid_image(file):
        raise TypeError()
    file.seek(0)

    if file.filename == '':
        raise FileExistsError()

    ext = file.filename.rsplit('.', 1)[-1].lower()

    if not (ext == 'jpg' or ext == 'jpeg' or ext == 'png' or ext == 'webp'):
        raise TypeError()
    
    filename = f"{uuid.uuid4().hex}.{ext}"

    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        if file:
            # 1. Pillow로 이미지 열기
            img = Image.open(file.stream)
            
            # 2. 이미지 처리 (예: 크기 조정)
            # (1) EXIF 기반으로 이미지 회전 (보정)
            # 이 함수가 내부적으로 90도, 180도, 270도 회전 및 대칭을 처리함
            img = ImageOps.exif_transpose(img)

            # (2) 1080px 리사이징
            if type == "feed":
                img.thumbnail((1080, 1080), Image.Resampling.LANCZOS)
            else:
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)

            # (3) RGB 모드로 변환
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 3. WebP로 저장
            filename_no_ext = os.path.splitext(filename)[0]
            webp_filename = f"{filename_no_ext}.webp"
            webp_path = os.path.join(UPLOAD_FOLDER, webp_filename)
            
            # quality: 1-100 (높을수록 화질 좋고 용량 큼)
            img.save(webp_path, 'webp', quality=82)
    except Exception as e:
        raise ValueError(e)
    
    return f"/static/uploads/{webp_filename}"