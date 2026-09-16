# Running the project in Zed and recording a five-minute explanation

## Start the project

1. In Zed, open the folder `C:\Users\LOQ15\alzikrayat-project`.
2. Press **Ctrl+Shift+P**, search for **workspace: new terminal**, and press Enter.
3. In the PowerShell terminal, run:

```powershell
cd C:\Users\LOQ15\alzikrayat-project
.\.venv\Scripts\python.exe run.py
```

The terminal should print:

```text
Alzikrayat is running at http://127.0.0.1:8000
```

4. Open http://127.0.0.1:8000 in your browser.
5. Keep this terminal running while using the website. Stop it with **Ctrl+C**.
6. After changing Python code, stop and run the same command again. Restarting the server logs users out, but keeps their database records and photos.

The command directly uses the Python environment that already contains the dependencies. You do not need to activate it separately, install everything again, recreate the database, or enter the MySQL command prompt. The MySQL Windows service must be running.

If the terminal reports that port 8000 is already in use, stop the earlier project server before starting another. If the application says the database is unavailable, open Windows Services and check that the MySQL service is running.

Zed reference: [Opening terminals](https://zed.dev/docs/terminal).

## Before recording

- Have Zed and the browser ready beside each other.
- Open the files listed in the screen cues so you can switch quickly.
- Use an account and a sample photo you are comfortable displaying.
- Keep the `.env` file closed because it contains database credentials.
- Read the spoken paragraphs only. The screen cues and timestamps are instructions for you.
- Aim for about 125 to 135 words per minute, with short pauses when changing files. Rehearse once and adjust your pace.
- The explanation describes the current plain-HTML version. It does not claim that Bootstrap, decorative design, or code comments are included.

## 0:00-0:35 — What the project does

**Show:** The website, followed by the project folder in Zed.

This project is a photo-sharing web application called Alzikrayat. Users can register, log in, upload photos, view other users' photos, and add comments. They can also delete their own photos. The browser interface uses plain HTML, a small amount of CSS, and JavaScript. Python handles requests and application logic, while MySQL stores the data. I will explain how a request moves through these parts and how the main features work.

## 0:35-1:15 — The project structure

**Show:** The models, controllers, and views folders in `C:\Users\LOQ15\alzikrayat-project\app`.

The code follows the Model, View, Controller pattern, usually called MVC. Models contain database queries and some validation rules. Views are the HTML templates displayed in the browser. Controllers connect the two: they receive a request, check what should happen, call the model, and choose a response.

There are also three application tiers. The browser is the presentation tier, Python is the application tier, and MySQL is the data tier. The browser communicates with Python over HTTP and never connects directly to the database.

## 1:15-1:55 — Starting the server and routing

**Show:** [run.py](C:/Users/LOQ15/alzikrayat-project/run.py), [server.py](C:/Users/LOQ15/alzikrayat-project/app/server.py), then [routes.py](C:/Users/LOQ15/alzikrayat-project/app/routes.py).

Running run dot py calls startServer in the server module. This starts Python's HTTP server, which reads requests and passes them to the router. The router is written manually using regular expressions instead of a web framework's routing system.

Each route has an HTTP method, a URL pattern, and a controller action. For example, a GET request for slash photo slash twelve captures twelve as the photo ID and calls the photo controller. GET requests normally display information, while POST requests submit forms and make changes.

## 1:55-2:40 — Settings and database access

**Show:** [config.py](C:/Users/LOQ15/alzikrayat-project/app/config.py), [database.py](C:/Users/LOQ15/alzikrayat-project/app/database.py), then [model.py](C:/Users/LOQ15/alzikrayat-project/app/models/model.py). Keep `.env` closed.

The configuration file reads database settings from the environment file. The database file uses those settings to create a MySQL connection through PyMySQL. The shared model provides functions for reading records and saving changes.

There are three tables: users, photos, and comments. A photo belongs to a user, and a comment belongs to both a user and a photo. Foreign keys maintain these relationships. Deleting a photo also deletes its related comments through a cascading foreign key.

Queries use placeholders, so input values are passed separately from the SQL statement. This helps prevent SQL injection.

## 2:40-3:35 — Registration, login, and cookies

**Show:** [user.py](C:/Users/LOQ15/alzikrayat-project/app/models/user.py), then [auth_controller.py](C:/Users/LOQ15/alzikrayat-project/app/controllers/auth_controller.py).

Registration validates the names, email, password, and password confirmation. Location, occupation, and biography are optional. The database also prevents duplicate email addresses.

Passwords are never stored as plain text. New accounts use PBKDF2 with a random salt to produce a password hash. Login hashes the supplied password using the stored salt and compares the result. The code also supports bcrypt hashes from existing accounts.

After successful login, Python creates a session and sends its random identifier in a cookie. The session remembers the logged-in user. Logout invalidates it. A separate cookie stores the last successful login time for seven days, so that information can still appear after logout.

## 3:35-4:20 — Uploading and deleting photos

**Show:** [photo_controller.py](C:/Users/LOQ15/alzikrayat-project/app/controllers/photo_controller.py), then the upload form and a photo detail page.

The photo controller first checks that the user is logged in. During an upload, Pillow checks whether the file can be read as an image. The application saves it as a JPEG with a generated filename. MySQL stores the filename, title, description, owner, and timestamp, rather than the image itself.

The gallery reads these records and displays links to individual photos. Before deletion, the controller checks that the current user owns the photo. It then coordinates deleting the database record and the physical file. Another user cannot delete a photo just by changing the URL.

## 4:20-5:00 — Comments and validation

**Show:** [comment_controller.py](C:/Users/LOQ15/alzikrayat-project/app/controllers/comment_controller.py), then [app.js](C:/Users/LOQ15/alzikrayat-project/public/js/app.js). If time allows, post one short comment.

Comments are saved with the current user's ID, the photo ID, and a timestamp. JavaScript submits the comment using fetch and updates the comments area without reloading the whole page.

Validation happens in three places: HTML form constraints, JavaScript checks, and Python checks. Server validation is necessary because browser checks can be bypassed. Jinja templates escape user text so it is displayed as text instead of executable HTML. POST forms also include a session token to help reject forged requests.

## Reading the simplified code

Read these in order:

1. [run.py](C:/Users/LOQ15/alzikrayat-project/run.py): starts the server.
2. [routes.py](C:/Users/LOQ15/alzikrayat-project/app/routes.py): matches a URL and selects an action.
3. [auth_controller.py](C:/Users/LOQ15/alzikrayat-project/app/controllers/auth_controller.py): start with loginForm, then login.
4. [user.py](C:/Users/LOQ15/alzikrayat-project/app/models/user.py): reads, validates, and saves users.
5. [login_form.html](C:/Users/LOQ15/alzikrayat-project/app/views/templates/auth/login_form.html): the actual HTML inputs.
6. [photo_controller.py](C:/Users/LOQ15/alzikrayat-project/app/controllers/photo_controller.py): uploadForm shows the form; upload saves the photo. deleteForm asks for confirmation; delete removes the photo.
7. [app.js](C:/Users/LOQ15/alzikrayat-project/public/js/app.js): validateField checks an input; saveComment sends a comment.
8. [server.py](C:/Users/LOQ15/alzikrayat-project/app/server.py): read the lower-level HTTP, session, cookie, and file-handling code last.

Displaying a form and processing its submission now use separate functions. The URL still uses GET to display and POST to submit. Form fields are written directly in HTML, without a custom form macro. The server remains handwritten; Flask is not used.
