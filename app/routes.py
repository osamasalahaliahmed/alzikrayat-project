import re

from app.controllers.auth_controller import AuthController
from app.controllers.comment_controller import CommentController
from app.controllers.home_controller import HomeController
from app.controllers.photo_controller import PhotoController

routes = [
    ("GET", r"/", HomeController.index),
    ("GET", r"/about", HomeController.about),
    ("GET", r"/login", AuthController.loginForm),
    ("POST", r"/login", AuthController.login),
    ("GET", r"/register", AuthController.registerForm),
    ("POST", r"/register", AuthController.register),
    ("POST", r"/logout", AuthController.logout),
    ("GET", r"/photos", PhotoController.index),
    ("GET", r"/photo/create", PhotoController.uploadForm),
    ("POST", r"/photo/store", PhotoController.upload),
    ("GET", r"/photo/([1-9][0-9]*)", PhotoController.show),
    ("GET", r"/photo/([1-9][0-9]*)/delete", PhotoController.deleteForm),
    ("POST", r"/photo/([1-9][0-9]*)/delete", PhotoController.delete),
    ("POST", r"/photo/([1-9][0-9]*)/comments", CommentController.create),
]


def dispatch(request):
    allowedMethods = []
    for method, pattern, action in routes:
        match = re.fullmatch(pattern, request.urlPath)
        if match:
            allowedMethods.append(method)
            if method == request.command:
                if match.groups():
                    photoId = int(match.group(1))
                    return action(request, photoId)
                return action(request)
    if allowedMethods:
        return request.errorPage(405, "This action does not support that request method.", {"Allow": ", ".join(allowedMethods)})
    request.errorPage(404, "The page you requested was not found.")

