FROM python:3.5.1
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y \
    libopenblas-dev \
    gfortran \
    pkg-config \
    libxmlsec1-dev \
    libhdf5-dev \
    libgeos-dev \
    build-essential \
    openssl \
    nginx \
    wget

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir numpy biopython pandas uwsgi 'Django==1.10.2' social-auth-app-django social-auth-core[saml] djangorestframework django-rest-swagger \
    django-filter django-taggit django-form-utils django-crispy-forms django-taggit-templatetags django-dirtyfields psycopg2 cython numexpr lxml requests requests-oauthlib \
    django-polymorphic celery[redis]==3.1.25 django-celery django-cleanup opbeat 'django-hstore==1.3.5' django-datatables-view django-oauth-toolkit simplejson \
    django-gravatar2 pygments xmltodict django-notifications-hq grpcio som sendgrid python3-saml biopython Pillow django-cors-headers

RUN mkdir /code
RUN mkdir -p /var/www/images
WORKDIR /code
ADD requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt
RUN /usr/bin/yes | pip uninstall cython
RUN apt-get remove -y gfortran

# Install crontab to setup job
RUN apt-get update && apt-get install -y gnome-schedule
#RUN echo "* * * * * /usr/bin/python /code/manage.py update_queue" >> /code/cronjob
RUN echo "0 0 * * * /usr/bin/python /code/manage.py calculate_rankings" >> /code/cronjob
RUN crontab /code/cronjob
RUN rm /code/cronjob

RUN apt-get autoremove -y
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ADD . /code/
CMD /code/run_uwsgi.sh

EXPOSE 3031
