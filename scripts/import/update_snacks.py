#!/usr/bin/env python

from docfish.apps.snacks.models import Snack
from docfish.apps.snacks.utils import upload_snack_image
from taggit.models import Tag
snacklink = 'https://docs.google.com/spreadsheets/d/1zFH7zct8wWvxtY1DYpuxfCD9wccmk7GQq7Y3yknr2GQ/pub?output=tsv'
import requests
import tempfile
import numpy
import pandas
import os

# check if a link exists
def link_exists(url):
    response = requests.get(url)
    if response.status_code == 404:
        return False
    return True

# download snackfile
download_folder = tempfile.mkdtemp()

def download_file(url,download_folder=None):
    '''download_file will download a url to a download folder.
    If no download folder is defined, a temporary one will be used
    and the downloaded file path returned.
    '''
    if download_folder == None:
        download_folder = tempfile.mkdtemp()
    filename = url.split('/')[-1]
    download_filename = "%s/%s" %(download_folder,filename)
    # NOTE the stream=True parameter
    response = requests.get(url, stream=True)
    with open(download_filename, 'wb') as filey:
        for chunk in response.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                filey.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
    return download_filename

snack_file = download_file(snacklink,download_folder)

snacks = pandas.read_csv(snack_file,sep='\t')
snacks.columns = ['timestamp','name','url','image']

for row in snacks.iterrows():
    # We only want urls that exist
    checks = [row[1].image,row[1].url]
    do_add = True
    for check in checks:
        if link_exists(check) == False:
            do_add = False
    name = row[1]['name'].lower().strip()
    if len(Snack.objects.filter(name=name)) > 0:
        do_add = False
    if do_add == True:
        snack,created = Snack.objects.update_or_create(name=row[1]['name'],
                                                       url=row[1]['url'])
        if created == True:
            snack.save()
        snack_image_file = download_file(row[1]['image'],download_folder)      
        snack = upload_snack_image(snack,snack_image_file)
