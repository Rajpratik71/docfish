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

    # Collections
    url(r'^collections$', views.view_collections, name="collections"),
    url(r'^collections/(?P<cid>\d+)/$',views.view_collection,name='collection_details'),
    url(r'^collections/(?P<cid>\d+)/explorer$',views.collection_explorer,name='collection_explorer'),
    url(r'^collections/(?P<cid>\d+)/stats/(?P<fieldtype>.+?)/detail$',views.collection_stats_detail,name='collection_stats_detail'),
    url(r'^collections/(?P<cid>\d+)/stats/$',views.collection_stats,name='collection_stats'),
    url(r'^collections/(?P<cid>\d+)/entities/delete$',views.delete_collection_entities,name='delete_collection_entities'),
    url(r'^collections/(?P<cid>\d+)/delete$',views.delete_collection,name='delete_collection'),
    url(r'^collections/(?P<cid>\d+)/edit$',views.edit_collection,name='edit_collection'),
    url(r'^collections/(?P<cid>\d+)/edit/privacy$',views.collection_change_privacy,
                                                   name='collection_change_privacy'),
    url(r'^collections/new$',views.edit_collection,name='new_collection'),
    url(r'^collections/my$',views.my_collections,name='my_collections'),

    # Collection Annotation/Markup Portal
    url(r'^collections/(?P<cid>\d+)/start$',views.collection_start,name='collection_start'), # all options
    url(r'^collections/(?P<cid>\d+)/instruction/update$',actions.collection_update_instruction,name='collection_update_instruction'),
    url(r'^collections/(?P<cid>\d+)/activate$',views.collection_activate,name='collection_activate'),
    url(r'^collections/(?P<cid>\d+)/(?P<fieldtype>.+?)/activate$',views.collection_activate,name='collection_activate'),

    # General
    url(r'^images/(?P<uid>\d+)/metadata$',actions.serve_image_metadata,name='serve_image_metadata'),
    url(r'^text/(?P<uid>\d+)/metadata$',actions.serve_text_metadata,name='serve_text_metadata'),
    url(r'^text/(?P<uid>\d+)/original$',actions.serve_text,name='serve_text'),

    # Labels
    url(r'^labels/(?P<cid>\d+)/new$',views.create_label,name='create_label'), # create new label
    url(r'^labels/(?P<cid>\d+)/(?P<lid>.+?)/new$',views.create_label,name='create_label'), # from existing
    url(r'^labels/(?P<cid>\d+)/view$',views.view_label,name='view_label'), # create new label
    url(r'^labels/(?P<cid>\d+)/(?P<lid>.+?)/remove$',views.remove_label,name='remove_label'), # from existin


    # Flag Images and Text
    url(r'^actions/images/(?P<uid>.+?)/flag$',actions.flag_image,name='flag_image'),
    url(r'^actions/text/(?P<uid>.+?)/flag$',actions.flag_text,name='flag_text'),
 
  
]
