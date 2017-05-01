from celery.decorators import periodic_task
from celery import shared_task, Celery
from celery.schedules import crontab

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.utils import timezone

from notifications.signals import notify
from docfish.settings import DOMAIN_NAME
from docfish.apps.main.models import *

from docfish.apps.users.utils import get_user
from docfish.apps.main.utils import get_collection
from docfish.apps.pubmed.database import (
    pull_articles,
    pull_images,
    pull_text
)

from docfish.settings import MEDIA_ROOT
from itertools import chain
import os
import tempfile
import shutil

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docfish.settings')
app = Celery('docfish')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@shared_task
def add_storage_articles(pmids,cid=None):
    '''add storage articles will retrieve a list of pubmed articles from storage,
    and if specified, add them to a collection. If the article is already represented
    in the database, it is added to the collection instead.
    '''
    if cid is not None:
        collection = get_collection(cid)
        collection_entities = collection.entity_set.all()

    pmids = format_pmids(pmids)
    entities = Entity.objects.filter(uid__in=pmids)
    present_ids = [x.uid for x in entities]
    request_ids = [x for x in pmids if x not in present_ids]
    articles = pull_articles(pmids)

    # Add all entities to collection set
    for entity in entities:
        if entity not in collection_entities:
            collection.entity_set.add(entity)
    collection.save()
    collection_entities = collection.entity_set.all()

    # Add new entities
    for article in articles:
        metadata = dict(article)
        entity,created = Entity.objects.get_or_create(uid=article['pmcid'],
                                                      defaults={'metadata':metadata})
        entity.save()
        images = pull_images(entity=article)
        texts = pull_text(entity=article)

        # Add images and text to entity
        for ds_image in images:
            metadata = dict(ds_image)
            image,created = ImageLink.objects.get_or_create(uid=ds_image['uid'],
                                                              entity=entity,
                                                              defaults={'metadata':metadata,
                                                                        'original':ds_image['url']})
            image.tags.add(ds_image['storage_contentType'])
            if ds_image['storage_contentType'].endswith('pdf'):
                image.tags.add('pdf')
            image.tags.save()
            image.save()            

        print("Added %s images for article %s" %(len(images),article['pmcid']))
        for ds_text in texts:
            metadata = dict(ds_text)
            text,created = TextLink.objects.get_or_create(uid=ds_text['uid'],
                                                            entity=entity,
                                                            defaults={'metadata':metadata,
                                                                      'original':ds_text['url']})
            text.tags.add(ds_text['storage_contentType'])
            if ds_text['storage_contentType'].endswith('xml'):
                text.tags.add('xml')
            text.tags.save()
            text.save()            

        print("Added %s texts for article %s" %(len(texts),article['pmcid']))
        entity.save()
        collection.entity_set.add(entity)

    collection.save()
    print("Added %s articles to collection %s" %(len(articles,collection.name)))
