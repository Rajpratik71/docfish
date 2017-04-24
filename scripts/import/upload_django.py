#!/usr/bin/env python

ftp_base = "ftp://ftp.ncbi.nlm.nih.gov/pub/pmc"
file_list = "ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_file_list.txt"

from django.core.files import File
from docfish.apps.main.models import (
    Collection, 
    Image, 
    Text,
    Entity
)
from django.contrib.auth.models import User
from glob import glob
from taggit.models import Tag
import requests
import signal
import xmltodict
import imghdr
import tempfile
import shutil
import tarfile
import numpy
import urllib
import pandas
import os
import re

# download lookup file
download_folder = tempfile.mkdtemp()

pmc_file = '%s/pmc.txt' %download_folder
urllib.request.urlretrieve(file_list, pmc_file)
pmc = pandas.read_csv(pmc_file,sep="\t",skiprows=1,header=None)

# oa_package/08/e0/PMC13900.tar.gz	Breast Cancer Res. 2001 Nov 2; 3(1):55-60	PMC13900	PMID:11250746	NO-CC CODE
pmc.columns = ["TARGZ_FILE","JOURNAL","PMCID","PMID","LICENSE"]
#pmc.to_csv('/code/scripts/pmc.tsv',sep="\t",index=None)
pmc = pandas.read_csv('/code/scripts/pmc.tsv',sep="\t")

# Associate with my username
owner = User.objects.get(username="vsochat")


def read_file(file_path):
    with open (file_path, "r") as myfile:
        return myfile.read().replace('\n', '')

def read_xml(xml_file):
    with open(xml_file) as fd:
        return xmltodict.parse(fd.read())

def create_images(article,images):
    for image in images:
        image_id = os.path.basename(image)
        new_image,created = Image.objects.get_or_create(entity=article,uid=image_id)
        with open(image,'rb') as filey:
             django_file = File(filey)
             new_image.original.save(image_id,
                                     django_file,save=True)
        extension = image.split('.')[-1]
        new_image.tags.add(extension)
        new_image.save()
     

def create_text(xml_file,article):
    content = read_file(xml_file)
    text_name = os.path.basename(xml_file)
    text,created = Text.objects.get_or_create(uid=text_name,
                                              entity=article,
                                              original=content)
    text.tags.add("article")
    text.tags.add("xml")
    text.save()
    return text


# TODO: some of these papers have movies (.mov) files
# might want to parse those too

def create_article(row,journal):
    pmid = row[1].PMID
    if not isinstance(pmid,str):
        if numpy.isnan(pmid):
            pmid = row[1].PMCID
    article,created = Entity.objects.get_or_create(uid=pmid,
                                                   collection=journal) 
    if created == True:
        tmpdir = tempfile.mkdtemp()
        download_url = "%s/%s" %(ftp_base,row[1].TARGZ_FILE)
        download_file = "/tmp/article.%s" %".".join(row[1].TARGZ_FILE.split('.')[1:])
        urllib.request.urlretrieve(download_url,download_file)
        tar = tarfile.open(download_file, "r:gz")
        tar.extractall(tmpdir)
        files = glob("%s/%s/*" %(tmpdir,row[1].PMCID))
        # Parse and create images
        images = [x for x in files if imghdr.what(x) is not None]
        pdf_files = [x for x in files if x.lower().endswith('pdf')]        
        xml_file = [x for x in files if x.lower().endswith('xml')][0]
        images = images + pdf_files
        create_images(article,images)
        # Create metadata and save with article
        metadata = {"PMC":row[1].PMCID,
                    "TYPE":"article",
                    "PUBLICATED_DATE": publication_date,
                    "DOWNLOAD_URL":download_url,
                    "LICENSE":row[1].LICENSE}
        if not isinstance(row[1].PMID,str):
            if not numpy.isnan(row[1].PMID):
                metadata['PMID'] = row[1].PMID
        article.metadata = metadata
        article.save()
        # Save xml as text
        text = create_text(xml_file,article)
        shutil.rmtree(tmpdir)
        return article
    return None

def signal_handler(signum, frame):
    raise Exception("Timed out!")

# Only allow each paper a 30 seconds to download
signal.signal(signal.SIGALRM, signal_handler)

timeouts = []
for row in pmc.iterrows():
    try:
        signal.alarm(30)
        journal_name = row[1].JOURNAL
        date_match = re.search("\d{4}",journal_name)
        publication_date = journal_name[date_match.start():]
        journal_name = journal_name[:date_match.start()].strip()
        journal,created = Collection.objects.get_or_create(name=journal_name,
                                                           owner=owner)
        if created == True:
            journal.metadata = {"TYPE":"journal"}
            journal.save()
        print("Adding %s %s of %s" %(row[1].PMID,row[0],pmc.shape[0]))
        article = create_article(row,journal)
    except:
        timeouts.append(row[0])
