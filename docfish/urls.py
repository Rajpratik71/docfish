'''
URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/

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
from django.conf.urls import include, url
from docfish.apps.base import urls as base_urls
from docfish.apps.main import urls as main_urls
from docfish.apps.main import collaborate as team_urls
from docfish.apps.users import urls as user_urls
from docfish.apps.api import urls as api_urls
from docfish.apps.storage import urls as storage_urls
from docfish.apps.pubmed import urls as pmc_urls
from docfish.apps.snacks import urls as snack_urls

from django.contrib import admin
#from django.contrib.sitemaps.views import sitemap, index

# Configure custom error pages
from django.conf.urls import ( handler404, handler500 )
handler404 = 'docfish.apps.base.views.handler404'
handler500 = 'docfish.apps.base.views.handler500'

# Sitemaps
#from docfish.apps.api.sitemap import ReportCollectionSitemap, ReportSitemap
#sitemaps = {"reports":ReportSitemap,
#            "collections":ReportCollectionSitemap}

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(base_urls)),
    url(r'^api/', include(api_urls)),
    url(r'^pmc/', include(pmc_urls)),
    url(r'^', include(main_urls)),
    url(r'^', include(team_urls)),
    url(r'^', include(user_urls)),
    url(r'^', include(snack_urls)),
    url(r'^upload/', include(storage_urls)),
#    url(r'^sitemap\.xml$', index, {'sitemaps': sitemaps}, name="sitemap"),
#    url(r'^sitemap-(?P<section>.+)\.xml$', sitemap, {'sitemaps': sitemaps},
#        name='django.contrib.sitemaps.views.sitemap'),
]
