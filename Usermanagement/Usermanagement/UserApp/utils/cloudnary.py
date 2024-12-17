from cloudinary.uploader import upload


def upload_file_to_cloudinary(
        file, folder_name, public_id, width=None, height=None, crop=None):
    try:
        cloudinary_response = upload(
            file,
            folder=folder_name,
            public_id=public_id,
            overwrite=True,
            width=width,
            height=height,
            crop=crop,
        )
        return cloudinary_response['secure_url']
    except Exception as e:
        raise ValueError(f"File upload failed : {str(e)}")
