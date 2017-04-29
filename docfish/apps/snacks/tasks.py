'''

Copyright (c) 2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

from celery.decorators import periodic_task
from celery import shared_task, Celery
from celery.schedules import crontab

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

from docfish.settings import DOMAIN_NAME

from docfish.apps.snacks.models import Snack

from datetime import datetime
from django.utils import timezone
import os
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docfish.settings')
app = Celery('docfish')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


def link_exists(url):
    response = requests.get(url)
    if response.status_code == 404:
        return False
    return True


@shared_task
def prune_dead_links():
    '''prune dead links will remove snacks with missing links
    '''
    snacks = Snack.objects.all()
    removed = []
    for snack in snacks:
        checks = [snack.url,snack.image,snack.thumbnail]
        for url in checks:
            if link_exists(url) == False:
                print("Removing %s" %snack.name)
                removed.append({"name": snack.name, "code": snack.code})
                snack.delete()
    return removed
