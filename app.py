"""Entry point: `python app.py` or `flask --app app run`. The application lives in `medical_expert/web/app.py`."""

from medical_expert.web.app import app

if __name__ == '__main__':
    app.run(debug=True, port=5000)
