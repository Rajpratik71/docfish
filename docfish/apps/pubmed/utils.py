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

from django.contrib.auth.decorators import login_required
from docfish.apps.users.utils import get_user
from Bio import Entrez
import xmltodict
import json
import sys


def read_cache(cache_pkl=None,combine=True):
    '''read_cache will read in a pickled cache of ids, helpful for querying 
    until we have a list that we know can be found'''
    cache_ids = None
    if cache_pkl is None:
        cache_pkl = '%s/docfish/apps/pubmed/data/pubmed_idcache.pkl' %(BASE_DIR)
    if os.path.exists(cache_pkl):
        cache_ids = pickle.load(open(id_cache,'rb'))
        if combine:
            cache_ids = cache_ids['pmid'] + cache_ids['pmc']
        cache_ids = set(cache_ids)
    return cache_ids


def search(query,email,retstart=0,retmax=100):
    '''do a search on behalf of a user. By default,
    we show 100 on a page at once, and start at 0'''

    Entrez.email = email
    handle = Entrez.esearch(db='pmc', 
                            sort='relevance', 
                            retmax=retmax,
                            retstart=retstart,
                            retmode='json', 
                            term=query)
    return json.loads(handle.read())


def fetch(id_list,email):
    ids = ','.join(id_list)
    handle = Entrez.efetch(db='pmc',
                           retmode='xml',
                           id=ids)
    papers = xmltodict.parse(handle.read())
    if 'pmc-articleset' in papers:
        if 'article' in papers['pmc-articleset']:
            return papers['pmc-articleset']['article']
    return None


def get(query,user,retstart=0,retmax=100,get_abstract=True):
    '''get is the base function to search and get a
    list of results. The user email is sniffed or
    a faux doc.fish alias returned
    '''
    done = True

    # We only can provide pmc open access content
    query = "%s AND open access[filter]" %(query)
    email = user.email
    if len(email) == 0 or email is None:
        email = "%s@doc.fish" %(user.username)

    results = search(query=query,
                     email=email,
                     retstart=retstart,
                     retmax=retmax)
    papers = None
    result_count = int(results['esearchresult']['count'])
    if result_count > 0:
        id_list = set(results['esearchresult']['idlist'])
        papers = fetch(id_list,email)
        papers = extract_articles(papers,get_abstract=get_abstract)

    return papers


def format_pmids(pmids,return_groups=False):
    '''format_pmids will take a list of identifiers, and
    for those that begin with PMC, classify as a pubmed central
    id. Those without PMC are parsed and returned as both PMC
    and PMID (since we use for searching)
    '''
    pmc_keys = []
    pmid_keys = []
    while len(pmids) > 0:
        key = pmids.pop()
        if key.startswith('PMC'):
            pmc_keys.append(key)
        else:
            pmc_keys.append("PMC%s" %key)
            pmid_keys.append("PMID:%s" %key)
    if return_groups:
        return {'pmc':pmc_keys,
                'pmid':pmid_keys}
    ids = pmc_keys + pmid_keys
    return ids


def extract_articles(papers,get_abstract=True):
    '''parse the json extracted xml (articles) and return in
    a more easy to digest json structure
    '''
    results = dict()
    if papers is not None:
        for article in papers:
            result = dict()
            result['journal'] = parse_journal(article)
            result['title'] = parse_title(article)
            if get_abstract:
                try:
                    result['abstract'] = parse_abstract(article)
                except:
                    result['abstract'] = "We weren't able to parse this abstract."
            try:
                uid = parse_id(article,id_name="pmc")
                uid = "PMC%s" %(uid)
            except:
                uid = parse_id(article,id_name="pmid")
                uid = "PMID:%s" %(uid)
            if uid is not None:
                results[uid] = result
    return results


def parse_journal(article):
    if 'journal-title' in article['front']['journal-meta']:
        title = article['front']['journal-meta']['journal-title']
    else:
        title = article['front']['journal-meta']['journal-title-group']['journal-title']
    if isinstance(title,dict):
        title = title['#text']
    return title


def parse_title(article):
    if 'article-title' in article['front']['article-meta']:
        title = article['front']['article-meta']['article-title']
    elif 'issue-title' in article['front']['article-meta']:
        title = article['front']['article-meta']['issue-title']
    else:
        title = article['front']['article-meta']['title-group']['article-title']
    if isinstance(title,dict):
        if "#text" in title:
            title = title['#text']
    return title


def parse_id(article,id_name=None):
    if id_name is None:
        id_name = 'pmc'
    meta = article['front']['article-meta']['article-id']
    if isinstance(meta,dict):
        meta = [meta]
    return [x['#text'] for x in meta if x['@pub-id-type']==id_name][0]


def parse_abstract(article):
    base = article['front']['article-meta']['abstract']
    if not isinstance(base,list):
        base = [base]
    abstract = []
    while len(base) > 0:
        chunk = base.pop(0)
        for section,content in chunk.items():
            if section == "sec":
                base = content + base
            elif section == "p":
                if not isinstance(content,list):
                    content = [content]
                text = []
                while len(content) > 0:
                    item = content.pop(0)
                    if isinstance(item,dict):
                        if "#text" in item:
                            text.append(item['#text']) 
                    elif isinstance(item,list):
                        content = item + content
                    else:
                        text.append(item)
                text = ''.join(text)
                abstract.append(text)
    return ''.join(abstract)
