FROM python:3.5

ARG BUILD_TYPE="Release"

COPY flaskr/ /flask_app/flaskr
COPY requirements.txt /flask_app
COPY test_endpoints.py /flask_app

WORKDIR /flask_app
EXPOSE 5000

RUN pip install -r requirements.txt

RUN  if [ "$BUILD_TYPE" = "Test" ] ; then pip install pytest ; fi

ENV  FLASK_APP flaskr
ENTRYPOINT ["flask","run","-h","0.0.0.0"]
