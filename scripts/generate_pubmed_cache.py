from som.api.google.storage.general import Client
from docfish.apps.pubmed.utils import format_pmids
from docfish.settings import GOOGLE_BUCKET_NAME
from google.cloud import datastore
from docfish.settings import BASE_DIR
import pickle

def get_client():
    return Client(bucket_name=GOOGLE_BUCKET_NAME)

client = get_client()

entities = client.get_entities()

pmid_list = [x['uid'].replace('PMID:','') for x in articles]
pmc_list = [x['pmcid'] for x in articles if 'pmcid' in x]
ids = {'pmc':pmc_list,'pmid':pmid_list}
id_cache = '%s/docfish/apps/pubmed/data/pubmed_idcache.pkl' %(BASE_DIR)
