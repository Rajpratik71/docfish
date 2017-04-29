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

from django.views.generic.base import TemplateView
from django.conf.urls import url, include

from rest_framework import routers
from rest_framework.authtoken import views as rest_views
from rest_framework_swagger.views import get_swagger_view

import docfish.apps.api.views as api_views
from docfish.settings import API_VERSION

router = routers.DefaultRouter()
router.register(r'^collection', api_views.CollectionViewSet)
router.register(r'^entity', api_views.EntityViewSet)
router.register(r'^image', api_views.ImageViewSet)
router.register(r'^text', api_views.TextViewSet)
router.register(r'^annotation', api_views.AnnotationViewSet)
router.register(r'^image-annotation', api_views.ImageAnnotationViewSet)
router.register(r'^text-annotation', api_views.TextAnnotationViewSet)
router.register(r'^image-markup', api_views.ImageMarkupViewSet)
router.register(r'^text-markup', api_views.TextMarkupViewSet)
router.register(r'^image-description', api_views.ImageDescriptionViewSet)
router.register(r'^text-description', api_views.TextDescriptionViewSet)
swagger_view = get_swagger_view(title='docfish API', url='')

urlpatterns = [

    # Wire up our API using automatic URL routing.
    url(r'^$', swagger_view),
    url(r'^', include(router.urls)),
    url(r'^token/$', api_views.token, name="token"),
    #url(r'^token/', api_views.get_token), # user token obtained in browser session
    url(r'^api-token-auth/', rest_views.obtain_auth_token), # user token obtained from command line
    # returns a JSON response when valid username and password fields are POSTed to the view using form data or JSON
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Always have default API view return current version
    #url(r'^docs$', api_views.api_view, name="api"),

    # Custom API views for single reports, report_sets
    #url(r'^report/(?P<report_id>.+?)$', api_views.ReportGet.as_view()),
    #url(r'^collections/set/(?P<set_id>.+?)/annotations$', api_views.set_annotations.as_view()),

    # JSON CALLS FOR VIEWS
    #url(r'^collection/(?P<cid>.+?)/counts$', api_views.get_annotation_counts), # user token obtained from command line
]
