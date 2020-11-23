FROM python:3.8.5-slim
WORKDIR /app
ENV FLASK_APP "loanapp"
COPY requirements.txt requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 80
COPY . .
CMD flask run --host=0.0.0.0
