import cloudinary
import cloudinary.uploader


class UploadFileService:
    def __init__(self, cloud_name, api_key, api_secret):
        """
        Initialize the UploadFileService.

        Args:
            cloud_name (str): The cloud name for Cloudinary.
            api_key (str): The API key for Cloudinary.
            api_secret (str): The API secret for Cloudinary.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Upload a file to Cloudinary.

        Args:
            file (UploadFile): The file to be uploaded.
            username (str): The username of the user.

        Returns:
            str: The URL of the uploaded file.
        """
        public_id = f"ContactsAPI/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
