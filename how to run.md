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
