from config.supabase_config import supabase

def upload_file(bucket_name, file_path, file_bytes, content_type="application/pdf"):
    """Uploads a file to Supabase Storage[cite: 230]."""
    try:
        response = supabase.storage.from_(bucket_name).upload(
            path=file_path,
            file=file_bytes,
            file_options={"content-type": content_type}
        )
        return response
    except Exception as e:
        print(f"Upload failed: {e}")
        return None

def get_public_url(bucket_name, file_path):
    """Generates a public URL for the frontend[cite: 247]."""
    return supabase.storage.from_(bucket_name).get_public_url(file_path)