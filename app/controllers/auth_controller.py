from datetime import datetime, timezone

import pymysql

from app.models.user import User


class AuthController:
    @staticmethod
    def loginForm(request):
        if request.user:
            return request.redirect("/photos")
        request.page("auth/login.html", title="Log in")

##Login logic
    @staticmethod
    def login(request):
        if request.user:
            return request.redirect("/photos")

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        account = None
        if email and len(email) <= 100:
            account = User.byEmail(email)

        if not account or not password or not User.checkPassword(password, account["password"]):
            return request.page(
                "auth/login.html", title="Log in", status=422,
                errors={"general": "The email or password is incorrect."},
                values=request.form,
            )

        user = User.find(account["id"])
        request.newSession(user)
        loginTime = datetime.now(timezone.utc).isoformat(timespec="seconds")
        request.setCookie("last_login", loginTime, 604800)
        request.redirect("/photos")

    @staticmethod
    def registerForm(request):
        if request.user:
            return request.redirect("/photos")
        request.page("auth/register.html", title="Create an account")

#register logic
    @staticmethod
    def register(request):
        if request.user:
            return request.redirect("/photos")

        errors = User.validate(request.form)
        if not errors:
            try:
                User.create(request.form)
                return request.redirect("/login?registered=1")
            except pymysql.IntegrityError as error:
                if error.args[0] != 1062:
                    raise
                errors["email"] = "An account with this email already exists."

        request.page(
            "auth/register.html", title="Create an account",
            status=422, errors=errors, values=request.form,
        )

    @staticmethod
    def logout(request):
        request.newSession()
        request.redirect("/login")
