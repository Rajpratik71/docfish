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
from docfish.apps.users.models import Team

from docfish.apps.users.utils import (
    summarize_teams_annotations
)

from datetime import datetime
from django.utils import timezone
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docfish.settings')
app = Celery('docfish')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@periodic_task(run_every=crontab(minute=0, hour=0))
def update_team_rankings():
    '''update team rankings will calculate ordered rank for all current teams, count annotations,
    and update these fields (with the update date) once a day at midnight (see above)
    '''
    teams = Team.objects.all()
    rankings = summarize_teams_annotations(teams) # sorted list with [(teamid,count)]

    # Iterate through rankings, get team and annotation count
    for g in range(len(rankings)):

        group = rankings[g]
        team_id = group[0]
        rank = g+1 # index starts at 0

        try:
            team = Team.objects.get(id=team_id)
        except:
            # A team not obtainable will be skipped
            continue

        team.annotation_count = group[1]
        team.ranking = rank
        team.metrics_updated_at = timezone.now()        
        team.save()
