import hmac
import json
import mimetypes
import secrets
import time
from datetime import datetime
from email import policy
from email.parser import BytesParser
from http.cookies import CookieError, SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlsplit

import pymysql
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config import appHost, appPort, projectFolder, uploadFolder
from app.routes import dispatch

templates = Environment(
    loader=FileSystemLoader(projectFolder / "app" / "views" / "templates"),
    autoescape=select_autoescape(["html"]),
)
sessions = {}


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handleRequest()

    def do_POST(self):
        self.handleRequest()

    def do_HEAD(self):
        self.handleRequest()

    def do_PUT(self):
        self.handleRequest()

    def do_DELETE(self):
        self.handleRequest()

    def setCookie(self, name, value, maxAge):
        cookie = SimpleCookie()
        cookie[name] = value
        cookie[name]["path"] = "/"
        cookie[name]["httponly"] = True
        cookie[name]["samesite"] = "Lax"
        cookie[name]["max-age"] = maxAge
        self.responseCookies.append(cookie[name].OutputString())

    def newSession(self, user=None):
        sessions.pop(self.sessionId, None)
        self.sessionId = secrets.token_urlsafe(32)
        self.session = {"user": user, "csrf": secrets.token_urlsafe(32), "expires": time.time() + 3600}
        sessions[self.sessionId] = self.session
        self.user = user
        self.setCookie("session_id", self.sessionId, 3600)

    def loadSession(self):
        self.cookies = SimpleCookie()
        try:
            self.cookies.load(self.headers.get("Cookie", ""))
        except CookieError:
            self.cookies = SimpleCookie()
        now = time.time()
        for sessionId in list(sessions):
            session = sessions.get(sessionId)
            if session and session["expires"] <= now:
                sessions.pop(sessionId, None)
        self.sessionId = ""
        if "session_id" in self.cookies:
            self.sessionId = self.cookies["session_id"].value
        self.session = sessions.get(self.sessionId)
        if self.session is None:
            self.newSession()
        self.user = self.session["user"]

    def readForm(self):
        contentLength = int(self.headers.get("Content-Length", "0"))
        if contentLength < 0:
            raise ValueError
        self.connection.settimeout(15)
        data = self.rfile.read(contentLength)
        if len(data) != contentLength:
            raise ValueError
        contentType = self.headers.get("Content-Type", "")
        if contentType.startswith("multipart/form-data"):
            message = BytesParser(policy=policy.default).parsebytes(
                b"Content-Type: " + contentType.encode("ascii") + b"\r\nMIME-Version: 1.0\r\n\r\n" + data
            )
            if not message.is_multipart() or message.defects:
                raise ValueError
            for part in message.iter_parts():
                name = part.get_param("name", header="content-disposition")
                if not name:
                    continue
                payload = part.get_payload(decode=True) or b""
                if part.get_filename() is not None:
                    self.files[name] = {"name": part.get_filename(), "data": payload}
                else:
                    self.form[name] = payload.decode("utf-8")
        elif contentType.startswith("application/x-www-form-urlencoded"):
            fields = parse_qs(data.decode("utf-8"), keep_blank_values=True)
            for name, values in fields.items():
                self.form[name] = values[0]
        else:
            raise ValueError

    def handleRequest(self):
        self.responseCookies = []
        self.form = {}
        self.files = {}
        self.user = None
        self.session = {}
        self.sessionId = ""
        self.cookies = SimpleCookie()
        url = urlsplit(self.path)
        self.urlPath = url.path
        self.query = {}
        for name, values in parse_qs(url.query).items():
            self.query[name] = values[0]
        self.wantsJson = "application/json" in self.headers.get("Accept", "")
        try:
            if self.urlPath.startswith("/static/"):
                if self.command not in ("GET", "HEAD"):
                    return self.errorPage(405, "Use GET to read this file.", {"Allow": "GET, HEAD"})
                return self.staticFile()
            self.loadSession()
            if self.urlPath.startswith("/media/"):
                if self.command not in ("GET", "HEAD"):
                    return self.errorPage(405, "Use GET to read this image.", {"Allow": "GET, HEAD"})
                if self.requireUser():
                    return self.mediaFile()
                return
            if self.command == "POST":
                self.readForm()
                submittedToken = self.form.get("csrf", "").encode("utf-8")
                sessionToken = self.session["csrf"].encode("utf-8")
                if not hmac.compare_digest(submittedToken, sessionToken):
                    return self.errorPage(403, "Your session changed. Refresh the page and try again.")
            dispatch(self)
        except (ValueError, UnicodeError):
            self.close_connection = True
            self.errorPage(400, "The request contains invalid data.")
        except pymysql.MySQLError:
            self.errorPage(503, "The database is unavailable. Please try again shortly.")
        except (BrokenPipeError, ConnectionResetError):
            pass
        except OSError:
            self.errorPage(500, "The image could not be read or saved. Please try again.")

    def requireUser(self):
        if self.user:
            return True
        if self.wantsJson:
            self.json({"error": "Please log in again before continuing."}, 401)
        else:
            self.redirect("/login")
        return False

    def respond(self, body, status=200, contentType="text/html; charset=utf-8", headers=None):
        data = body
        if isinstance(body, str):
            data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", contentType)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("Cache-Control", "no-store")
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        for cookie in self.responseCookies:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def render(self, templateName, **values):
        lastLogin = None
        if "last_login" in self.cookies:
            try:
                lastLogin = datetime.fromisoformat(self.cookies["last_login"].value).strftime("%d %b %Y at %H:%M UTC")
            except ValueError:
                pass
        context = {
            "user": self.user, "csrf": self.session.get("csrf", ""), "query": self.query,
            "lastLogin": lastLogin, "errors": {}, "values": {}, "title": "Alzikrayat",
        }
        context.update(values)
        return templates.get_template(templateName).render(**context)

    def page(self, templateName, status=200, **values):
        self.respond(self.render(templateName, **values), status)

    def errorPage(self, status, message, headers=None):
        if self.wantsJson:
            return self.json({"error": message}, status)
        self.respond(self.render("error.html", title=str(status), status=status, message=message), status, headers=headers)

    def redirect(self, location):
        self.respond(b"", 303, headers={"Location": location})

    def json(self, data, status=200):
        self.respond(json.dumps(data), status, "application/json; charset=utf-8")

    def staticFile(self):
        staticFolder = projectFolder / "public"
        filePath = (staticFolder / unquote(self.urlPath.removeprefix("/static/"))).resolve()
        if not filePath.is_relative_to(staticFolder.resolve()) or filePath.is_relative_to(uploadFolder.resolve()) or not filePath.is_file():
            return self.errorPage(404, "This file was not found.")
        if filePath.suffix.lower() not in (".css", ".js", ".svg", ".png", ".jpg"):
            return self.errorPage(404, "This file was not found.")
        self.respond(filePath.read_bytes(), contentType=mimetypes.guess_type(filePath)[0] or "application/octet-stream")

    def mediaFile(self):
        fileName = unquote(self.urlPath.removeprefix("/media/"))
        filePath = (uploadFolder / fileName).resolve()
        if not filePath.is_relative_to(uploadFolder.resolve()) or filePath.name.startswith(".") or not filePath.is_file():
            return self.errorPage(404, "This image was not found.")
        if filePath.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            return self.errorPage(404, "This image was not found.")
        self.respond(filePath.read_bytes(), contentType=mimetypes.guess_type(filePath)[0] or "image/jpeg")


def startServer():
    with ThreadingHTTPServer((appHost, appPort), RequestHandler) as server:
        print(f"Alzikrayat is running at http://{appHost}:{appPort}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


