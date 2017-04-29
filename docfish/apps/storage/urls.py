# encoding: utf-8
from django.conf.urls import url
import docfish.apps.storage.views as upload_views

urlpatterns = [
    url(r'^(?P<cid>\d+)/new$', upload_views.UploadDatasets.as_view(), name='upload_datasets'),
    url(r'^clear/$', upload_views.clear_database, name='clear_database'),
]
