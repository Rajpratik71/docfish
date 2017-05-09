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

from django.conf.urls import url
import docfish.apps.main.views as views
import docfish.apps.main.actions as actions

urlpatterns = [

    # Collections (user) markup of images and text
    url(r'^collections/(?P<cid>\d+)/images/markup$',views.collection_markup_image,name='collection_markup_image'),
    url(r'^collections/(?P<cid>\d+)/text/markup$',views.collection_markup_text,name='collection_markup_text'),

    # Collections (user) save of a single markup
    url(r'^collections/(?P<cid>\d+)/images/(?P<uid>.+?)/markup$',views.markup_image,name='markup_image'),
    url(r'^collections/(?P<cid>\d+)/text/(?P<uid>.+?)/markup$',views.markup_text,name='markup_text'),

    # Note, updates for team markups means that team_id is included in the post.
    url(r'^markup/(?P<cid>\d+)/entity/(?P<uid>\d+)/text/update$',actions.update_text_markup,name='update_text_markup'),    

    # Teams Markup - first browse (no collaborative annotation)
    url(r'^teams/(?P<tid>\d+)/collection/(?P<cid>\d+)/text/markup$',views.markup_text,name='markup_text'),
    # images (not yet implemented)
    #url(r'^teams/(?P<tid>\d+)/collection/(?P<cid>\d+)/text/markup$',views.markup_image,name='markup_image'),

    # Teams markup (collaboration after first)
    url(r'^teams/(?P<tid>\d+)/collection/(?P<cid>\d+)/text/(?P<uid>\d+)/markup$',views.markup_text,name='markup_text'),
    #url(r'^teams/(?P<tid>\d+)/collection/(?P<cid>\d+)/images/(?P<uid>\d+)/markup$',views.markup_image,name='team_markup_image'),

]
