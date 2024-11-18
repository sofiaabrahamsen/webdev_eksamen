FROM python:3.10.14
WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# CMD python app.py
# CMD gunicorn --reload --workers 4 --bind 0.0.0.0:80 app:application
# CMD gunicorn --reload --workers 1 --bind 0.0.0.0:80 app:application
CMD python -m bottle --debug --reload --server paste --bind 0.0.0.0:80 app:application