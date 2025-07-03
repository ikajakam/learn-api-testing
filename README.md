# API Playground - Practice JWT, SQLi, XSS & IDOR


## This is a deliberately vulnerable app built for learning.
A hands-on API hacking lab built with Python & Flask — learn and practice exploiting real-world bugs like XSS, SQLi, JWT abuse, IDOR, Authentication and more in one breakable app.

## TEST LIVE  https://tarkash.surapura.in/

![Made for Learning](https://img.shields.io/badge/made%20for-learning-blueviolet) ![API Security](https://img.shields.io/badge/focus-API%20Security-yellowgreen)  ![Python](https://img.shields.io/badge/built%20with-Python%20%26%20Flask-3776AB) ![CTF](https://img.shields.io/badge/type-CTF-informational)

![XSS](https://img.shields.io/badge/XSS-red) ![SQLi](https://img.shields.io/badge/SQLi-orange) ![JWT](https://img.shields.io/badge/JWT-blue) ![IDOR](https://img.shields.io/badge/IDOR-lightgrey) ![File Upload](https://img.shields.io/badge/Authentication-cyan) ![File Upload](https://img.shields.io/badge/File%20Upload-critical)







##  🚀 Explore
- 🧾 **/api/register** — Create a user account (safe).
- 🔐 **/api/login** — Auth via secure JWT (in-memory) and vulnerable SQL-based login.
- 📤 **/api/upload** — Upload files with checks.
- 🧠 **/api/form?id=0** — Interesting `id=0` behavior (custom logic).
- ⚠️ **/api/form?id=X** — Test IDOR & XSS via form viewer.
- 📦 **/view-form?id=X** — Stored XSS rendered on page.
- 🔎 **Request Logs** — Every request is logged with IP, method, headers, etc.
#
# Get an Access Token (cURL Format)
### Use these curl commands in your terminal to register and login :

### Register a new user

```bash
curl -X POST https://tarkash.surapura.in/api/register \\
     -H "Content-Type: application/json" \\
     -d '{"username": "masino", "password": "tamburo"}'
```

### Login
```bash
curl -X POST https://tarkash.surapura.in/api/login \\
     -H "Content-Type: application/json" \\
     -d '{"username": "masino", "password": "tamburo"}'
```
#### The response will look like:
```bash
  {"token":"your-jwt-token"}
  ```
- Save the token. Use it as a Bearer token for all other requests.

### Submit a Form (Find the special id=0 flag!)
```bash
curl -X PUT "https://tarkash.surapura.in/api/form?id=0" \\
     -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \\
     -H "Content-Type: application/json" \\
     -d '{"username":"masino","name":"tamburo","email":"bhootnike","message":"<img src=\"x\" onerror=\"alert(1)\">"}'
```
- Explore and tamper with id=0. Understand response logic, bypasses, and constraints

### File Upload Endpoint
```bash
curl -X POST "https://tarkash.surapura.in/api/upload" \\
     -H "Content-Type: application/json" \\
     -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \\
     -F "file=@/path/to/your/file.jpg"
```
- /uploads/yourfile.jpg

## Practice Flow
- Step 1: Register at https://tarkash.surapura.in/api/register with a JSON body like {"username": "test", "password": "pass"}
- Step 2: Login via /api/login and receive your JWT token
- Step 3: Submit a form with a message field to /api/form
- Step 4: View / Edit submitted forms via /api/form?id=1 and exploit IDOR and stored XSS
- Step 5: Visit /view-form?id=1 to render and trigger your payload (stored XSS)

##### POP that XSS
##### Submit form with id=0

#
# HOW TO RUN

## Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```
## Install Requirements
```bash
pip install flask pyjwt werkzeug pytz
```
## Run the Server
``` bash
python3 app_formsubmit.py
```
- By default, the app runs on: `http://127.0.0.1:5000`

-   `uploads/` folder will be created automatically
-   Logs are saved to `app.log`
-   Ensure write access to working directory


#### will update more vulnerable routes - suggestions are welcome


