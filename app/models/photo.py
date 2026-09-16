from app.models.model import Model


class Photo(Model):
    @staticmethod
    def all(userId=None):
        sql = (
            "SELECT photos.*, users.first_name, users.last_name FROM photos "
            "JOIN users ON users.id=photos.user_id"
        )
        if userId is not None:
            return Photo.fetch(sql + " WHERE photos.user_id=%s ORDER BY photos.date_time DESC,photos.id DESC", (userId,))
        return Photo.fetch(sql + " ORDER BY photos.date_time DESC,photos.id DESC")

    @staticmethod
    def find(photoId):
        return Photo.fetch(
            "SELECT photos.*,users.first_name,users.last_name FROM photos JOIN users ON users.id=photos.user_id WHERE photos.id=%s",
            (photoId,), one=True,
        )

    @staticmethod
    def count():
        return Photo.fetch("SELECT COUNT(*) AS total FROM photos", one=True)["total"]

    @staticmethod
    def delete(photoId, userId, connection):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM photos WHERE id=%s AND user_id=%s", (photoId, userId))
            return cursor.rowcount

    @staticmethod
    def validate(data):
        errors = {}
        title = data.get("title", "").strip()
        if not title or len(title) > 200:
            errors["title"] = "Enter a title of 1 to 200 characters."
        if len(data.get("description", "")) > 2000:
            errors["description"] = "Use no more than 2,000 characters."
        return errors

    @staticmethod
    def create(userId, fileName, title, description):
        return Photo.execute(
            "INSERT INTO photos (user_id,file_name,title,description) VALUES (%s,%s,%s,%s)",
            (userId, fileName, title, description),
        )

