from app.models.model import Model


class Comment(Model):
    @staticmethod
    def forPhoto(photoId):
        return Comment.fetch(
            "SELECT comments.*,users.first_name,users.last_name FROM comments JOIN users ON users.id=comments.user_id "
            "WHERE comments.photo_id=%s ORDER BY comments.date_time,comments.id",
            (photoId,),
        )

    @staticmethod
    def count():
        return Comment.fetch("SELECT COUNT(*) AS total FROM comments", one=True)["total"]

    @staticmethod
    def create(photoId, userId, text):
        return Comment.execute(
            "INSERT INTO comments (photo_id,user_id,comment) VALUES (%s,%s,%s)",
            (photoId, userId, text),
        )

