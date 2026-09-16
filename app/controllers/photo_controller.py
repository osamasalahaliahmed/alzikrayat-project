import io
import uuid
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError

from app.config import uploadFolder
from app.database import getConnection
from app.models.comment import Comment
from app.models.photo import Photo
from app.models.user import User


class PhotoController:
    @staticmethod
    def index(request):
        if not request.requireUser():
            return

        userId = request.query.get("user")
        if request.query.get("mine") == "1":
            userId = request.user["id"]

        owner = None
        if userId is not None:
            try:
                userId = int(userId)
                if userId < 1:
                    raise ValueError
            except ValueError:
                return request.errorPage(400, "Choose a valid user.")

            owner = User.find(userId)
            if not owner:
                return request.errorPage(404, "This user was not found.")

        photos = Photo.all(userId)
        request.page("photos/index.html", title="Photos", photos=photos, owner=owner)

    @staticmethod
    def show(request, photoId):
        if not request.requireUser():
            return

        photo = Photo.find(photoId)
        if not photo:
            return request.errorPage(404, "This photo was not found.")

        comments = Comment.forPhoto(photoId)
        request.page("photos/show.html", title=photo["title"], photo=photo, comments=comments)

    @staticmethod
    def uploadForm(request):
        if not request.requireUser():
            return
        request.page("photos/create.html", title="Upload a photo")

    @staticmethod
    def upload(request):
        if not request.requireUser():
            return

        errors = Photo.validate(request.form)
        upload = request.files.get("photo")
        image = None

        if not upload or not upload["data"]:
            errors["photo"] = "Choose an image."
        else:
            image = PhotoController.readImage(upload["data"])
            if image is None:
                errors["photo"] = "This file cannot be read as an image."

        if errors:
            if image is not None:
                image.close()
            return request.page(
                "photos/create.html", title="Upload a photo",
                status=422, errors=errors, values=request.form,
            )

        fileName = uuid.uuid4().hex + ".jpg"
        filePath = uploadFolder / fileName
        title = request.form["title"].strip()
        description = request.form.get("description", "").strip()

        try:
            image.save(filePath, "JPEG", quality=90)
            photoId = Photo.create(request.user["id"], fileName, title, description)
        except Exception:
            filePath.unlink(missing_ok=True)
            raise
        finally:
            image.close()

        request.redirect(f"/photo/{photoId}?uploaded=1")

    @staticmethod
    def readImage(data):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(data)) as image:
                    image.load()
                    return ImageOps.exif_transpose(image).convert("RGB")
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
            return None

    @staticmethod
    def getOwnedPhoto(request, photoId):
        if not request.requireUser():
            return None

        photo = Photo.find(photoId)
        if not photo:
            request.errorPage(404, "This photo was not found.")
            return None
        if photo["user_id"] != request.user["id"]:
            request.errorPage(403, "You can only delete your own photos.")
            return None
        return photo

    @staticmethod
    def deleteForm(request, photoId):
        photo = PhotoController.getOwnedPhoto(request, photoId)
        if photo:
            request.page("photos/delete.html", title="Delete photo", photo=photo)

    @staticmethod
    def delete(request, photoId):
        photo = PhotoController.getOwnedPhoto(request, photoId)
        if not photo:
            return

        filePath = (uploadFolder / photo["file_name"]).resolve()
        if not filePath.is_relative_to(uploadFolder.resolve()):
            return request.errorPage(400, "The stored image path is invalid.")

        temporaryPath = filePath.with_name(".deleting-" + uuid.uuid4().hex)
        with getConnection() as connection:
            try:
                deletedRows = Photo.delete(photoId, request.user["id"], connection)
                if deletedRows != 1:
                    return request.errorPage(404, "This photo was already deleted.")
                if filePath.exists():
                    filePath.rename(temporaryPath)
                connection.commit()
            except Exception:
                connection.rollback()
                if temporaryPath.exists():
                    temporaryPath.rename(filePath)
                raise

        temporaryPath.unlink(missing_ok=True)
        request.redirect("/photos?deleted=1")
