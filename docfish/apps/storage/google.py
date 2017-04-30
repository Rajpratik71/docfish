'''

google.py basic functions for using som (stanford open modules) to query Google
Datastore and storage

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

from som.api.google.storage.general import Client
from docfish.settings import GOOGLE_BUCKET_NAME
from google.cloud import datastore

def get_client():
    return Client(bucket_name=GOOGLE_BUCKET_NAME)


def pull_articles(pmids,client=None,limit=None):
    '''pull articles will return a subset of datastore 
    articles by way of searching on the index fields 
    pmcid and uid. If an article is not found, it is
    not returned'''

    if client is None:
        client = get_cleint()

    if not isinstance(pmids,list):
        pmids = [pmids]

    pmid_keys = ['PMID:%s' %k for k in pmids]
    pmc_keys = ["PMC%s" %k for k in pmids]

    articles = []
    pmc_articles = client.get_entities(uids=pmc_keys,field="pmcid")
    pmid_articles = client.get_entities(uids=pmid_keys,field="uid")

    if pmc_articles is not None:
        articles = articles + pmc_articles
    if pmid_articles is not None:
        articles = articles + pmid_articles

    return articles



def pull_images(entity):
    if not isinstance(entity,datastore.Entity):
        try:
            entity = pull_articles(entity)[0]
        except:
            return None
    return client.get_images(entity)


   
def pull_text():
    if not isinstance(entity,datastore.Entity):
        try:
            entity = pull_articles(entity)[0]
        except:
            return None
    return client.get_text(entity)
