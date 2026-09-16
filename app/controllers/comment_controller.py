from app.models.comment import Comment
from app.models.photo import Photo


class CommentController:
    @staticmethod
    def create(request, photoId):
        if not request.requireUser():
            return
        if not Photo.find(photoId):
            return request.json({"error": "This photo was not found."}, 404)
        commentText = request.form.get("comment", "").strip()
        if not commentText or len(commentText) > 2000:
            return request.json({"error": "Write a comment of 1 to 2,000 characters."}, 422)

        userId = request.user["id"]
        Comment.create(photoId, userId, commentText)

        if request.wantsJson:
            comments = Comment.forPhoto(photoId)
            html = request.render("photos/comments.html", comments=comments)
            return request.json({"html": html})

        request.redirect(f"/photo/{photoId}#comments")

