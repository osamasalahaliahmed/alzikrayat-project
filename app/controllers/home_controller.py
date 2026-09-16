from app.models.comment import Comment
from app.models.photo import Photo
from app.models.user import User


class HomeController:
    @staticmethod
    def index(request):
        counts = {
            "users": User.count(),
            "photos": Photo.count(),
            "comments": Comment.count(),
        }
        request.page("home.html", title="Home", counts=counts)

    @staticmethod
    def about(request):
        request.page("about.html", title="About us")

