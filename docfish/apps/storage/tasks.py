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

from som.wordfish.validators import (
    validate_folder,
    validate_compressed
)

from som.wordfish.structures import (
    structure_compressed
)

from docfish.apps.users.utils import get_user
from docfish.apps.main.utils import get_collection
from docfish.apps.storage.google import (
    pull_articles,
    pull_images,
    pull_text
)

from docfish.apps.storage.utils import (
    extract_tmp,
    import_structures
)

from docfish.settings import MEDIA_ROOT
from datetime import datetime
from itertools import chain
import os
import tempfile
import shutil

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docfish.settings')
app = Celery('docfish')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@shared_task
def test_worker(printme):
    '''test worker is a dummy function to print some output to the console.
    You should be able to see it via docker-compose logs worker
    '''
    print(printme)


@shared_task
def validate_dataset_upload(compressed_file,remove_folder=False):
    '''validate_dataset_upload will take an compressed file object, decompress
    it, and validate it for correctness. If it's valid, it will return true, 
    and another job can actually upload the dataset (so there is no
    delay on the front end) 
    :param compressed_file: a string path to a file to test.
    '''
    tmpdir = os.path.dirname(compressed_file)
    valid = validate_compressed(compressed_file)
    result = {'valid':valid,
              'file':compressed_file}
    if remove_folder == True:
        shutil.rmtree(tmpdir)
    return result


@shared_task
def dataset_upload(compressed_file,cid):
    '''dataset_upload will take an compressed file object, decompress
    it, (again) validate it for correctness, and then upload the dataset.
    '''
    tmpdir = os.path.dirname(compressed_file)
    collection = get_collection(cid)
    if validate_compressed(compressed_file) == True:
  
        # Now we add entities to the collection
        structures = structure_compressed(compressed_file,
                                          testing_base=tmpdir,
                                          clean_up=False)  

        collection = import_structures(structures,collection)

    shutil.rmtree(tmpdir)


@shared_task
def validate_memory_upload(memory_file,collection):
    '''validate_upload will first validate an uploaded (compressed) file
    for validity. If it's valid, it fires off a job to extract data
    to a collection. If not valid, it returns the error message to
    the user.
    :param memory_file: the in memory uploaded file
    :param collection: the collection to add the uploaded dataset to
    '''
    data = {'is_valid': False, 'name': 'Invalid', 'url': ""}

    tmpdir = "%s/tmp" %MEDIA_ROOT
    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)
    compressed_file = extract_tmp(memory_file,base_dir=tmpdir)
    result = validate_dataset_upload(compressed_file)

    if result['valid'] == True:
        dataset_upload.apply_async(kwargs={"compressed_file": result['file'],
                                           "cid":collection.id })

        name = os.path.basename(result['file'])
        data = {'is_valid': True, 'name': name, 'url': collection.get_absolute_url()}

    else:
        tmpdir = os.path.dirname(result['file'])
        shutil.rmtree(tmpdir)

    return data



@shared_task
def add_storage_articles(pmids,cid=None):
    '''add storage articles will retrieve a list of pubmed articles from storage,
    and if specified, add them to a collection. If the article is already represented
    in the database, it is added to the collection instead.
    '''
    if cid is not None:
        collection = get_collection(cid)
        collection_entities = collection.entity_set.all()

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
