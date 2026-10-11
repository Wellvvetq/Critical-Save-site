import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "webp", "gif", "svg"})

def save_media_file(file_storage) -> str:
    """
    Saves an uploaded file with randomized secure filename.
    Returns relative web path (e.g., '/static/uploads/uuid.png')
    """
    if not file_storage or not file_storage.filename:
        return None
        
    if not allowed_file(file_storage.filename):
        raise ValueError("Disallowed file format. Allowed: PNG, JPG, JPEG, WEBP, GIF, SVG.")
        
    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex[:16]}.{ext}"
    
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    
    dest_path = os.path.join(upload_dir, unique_name)
    file_storage.save(dest_path)
    
    return f"/static/uploads/{unique_name}"
