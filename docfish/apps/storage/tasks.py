from celery.decorators import periodic_task
from celery import shared_task, Celery
from celery.schedules import crontab

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.utils import timezone

from notifications.signals import notify
from docfish.settings import DOMAIN_NAME
from docfish.apps.main.models import (
    Collection,
    Entity,
    Image,
    Text
)

from som.wordfish.validators import (
    validate_folder,
    validate_compressed
)

from som.wordfish.structures import (
    structure_compressed
)

from docfish.apps.users.utils import get_user
from docfish.apps.main.utils import get_collection
from docfish.apps.storage.google import pull_articles

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

    # First generate a list of entities
    request_ids = []

     # TODO: quick way determine if entity not in list...
    entities = Entity.objects.filter(uid__in=pmids)

    present_ids = [x.uid for x in entities]
    keys = [x for x in pmids if x not in entities]    

    articles = pull_articles(pmids)


    # Use client to get response of all missing
