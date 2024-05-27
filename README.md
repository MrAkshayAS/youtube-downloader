## Project Structure

Assuming your Flask project structure will look like this:

```bash
project-root/
│
├── static/
│   └── (static files like CSS, JS, etc.)
│
├── templates/
│   ├── partials
│   │  ├── _header.html
│   │  └── _footer.html
│   ├── home.html
│   └── single_video.html
│
├── app.py
├── requirements.txt
└── README.md
```

### Step-by-Step Setup

#### 1. Environment Setup

Make sure you have Python installed. You can create a virtual environment for this project to manage dependencies cleanly:

```bash
python -m venv venv
```
### 2. Install Dependencies
```bash
flask==3.0.1
google-api-python-client
gunicorn
waitress # For production deployment on Windows
```

### 3. API Keys
Ensure you have a Google API key with YouTube Data API v3 enabled. Set it as an environment variable:
#### For Windows
```bash
$env:GOOGLE_API_KEY="your_api_key_here"
```
#### For Unix/Linux/MacOS:
```bash
export GOOGLE_API_KEY="your_api_key_here"
```
Replace "your_api_key_here" with your actual API key.
