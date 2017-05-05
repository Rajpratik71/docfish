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
from django.views.generic.base import TemplateView
import docfish.apps.main.views as views
import docfish.apps.main.actions as actions

urlpatterns = [

    # Collections and entities
    url(r'^collections$', views.view_collections, name="collections"),
    url(r'^collections/(?P<cid>\d+)/entity/(?P<eid>.+?)/details$',views.view_entity,name='entity_details'),
    url(r'^collections/(?P<cid>\d+)/entity/(?P<eid>.+?)/remove$',views.remove_entity,name='remove_entity'),

    # Collections
    url(r'^collections/(?P<cid>\d+)/$',views.view_collection,name='collection_details'),
    url(r'^collections/(?P<cid>\d+)/explorer$',views.collection_explorer,name='collection_explorer'),
    url(r'^collections/(?P<cid>\d+)/stats/(?P<fieldtype>.+?)/detail$',views.collection_stats_detail,name='collection_stats_detail'),
    url(r'^collections/(?P<cid>\d+)/stats/$',views.collection_stats,name='collection_stats'),
    url(r'^collections/(?P<cid>\d+)/entities/delete$',views.delete_collection_entities,name='delete_collection_entities'),
    url(r'^collections/(?P<cid>\d+)/delete$',views.delete_collection,name='delete_collection'),
    url(r'^collections/(?P<cid>\d+)/edit$',views.edit_collection,name='edit_collection'),
    url(r'^collections/(?P<cid>\d+)/edit/privacy$',views.collection_change_privacy,
                                                   name='collection_change_privacy'),
    #url(r'^collections/(?P<cid>.+?)/entities/upload$',views.upload_entities,name='upload_entities'),
    url(r'^collections/new$',views.edit_collection,name='new_collection'),
    url(r'^collections/my$',views.my_collections,name='my_collections'),

    # Collection Annotation/Markup Portal
    url(r'^collections/(?P<cid>\d+)/start$',views.collection_start,name='collection_start'), # all options
    url(r'^collections/(?P<cid>\d+)/instruction/update$',actions.collection_update_instruction,name='collection_update_instruction'),
    url(r'^collections/(?P<cid>\d+)/activate$',views.collection_activate,name='collection_activate'),
    url(r'^collections/(?P<cid>\d+)/(?P<fieldtype>.+?)/activate$',views.collection_activate,name='collection_activate'),
    url(r'^images/(?P<uid>\d+)/metadata$',actions.serve_image_metadata,name='serve_image_metadata'),
    url(r'^text/(?P<uid>\d+)/metadata$',actions.serve_text_metadata,name='serve_text_metadata'),
    url(r'^text/(?P<uid>\d+)/original$',actions.serve_text,name='serve_text'),

    # Annotation Labels
    url(r'^labels/(?P<cid>\d+)/new$',views.create_label,name='create_label'), # create new label
    url(r'^labels/(?P<cid>\d+)/(?P<lid>.+?)/new$',views.create_label,name='create_label'), # from existing
    url(r'^labels/(?P<cid>\d+)/view$',views.view_label,name='view_label'), # create new label
    url(r'^labels/(?P<cid>\d+)/(?P<lid>.+?)/remove$',views.remove_label,name='remove_label'), # from existin

    # Change / add contributors
    url(r'^contributors/(?P<cid>\d+)/(?P<uid>.+?)/remove$',views.remove_contributor,name='remove_contributor'),
    url(r'^contributors/(?P<cid>\d+)/add$',views.add_contributor,name='add_contributor'),
    url(r'^contributors/(?P<cid>\d+)/edit$',views.edit_contributors,name='edit_contributors'),

    # Collection image markup and annotation (users)
    url(r'^collections/(?P<cid>\d+)/images/markup$',views.collection_markup_image,name='collection_markup_image'),
    url(r'^collections/(?P<cid>\d+)/images/describe$',views.collection_describe_image,name='collection_describe_image'),
    url(r'^collections/(?P<cid>\d+)/images/(?P<uid>.+?)/markup$',views.markup_image,name='markup_image'),
    url(r'^collections/(?P<cid>\d+)/images/(?P<uid>\d+)/describe$',views.describe_image,name='describe_image'),
    url(r'^collections/(?P<cid>\d+)/images/annotate$',views.collection_annotate_image,name='collection_annotate_image'),

    # Update Annotations and Markup
    url(r'^annotate/(?P<cid>\d+)/entity/(?P<uid>\d+)/images/update$',views.update_image_annotation,name='update_image_annotation'),
    url(r'^annotate/(?P<cid>\d+)/entity/(?P<uid>\d+)/images/clear$',views.clear_image_annotations,name='clear_image_annotations'),
    url(r'^annotate/(?P<cid>\d+)/entity/(?P<uid>\d+)/text/update$',views.update_text_annotation,name='update_text_annotation'),
    url(r'^annotate/(?P<cid>\d+)/entity/(?P<uid>\d+)/text/clear$',views.clear_text_annotations,name='clear_text_annotations'),
    url(r'^markup/(?P<cid>\d+)/entity/(?P<uid>\d+)/text/update$',actions.update_text_markup,name='update_text_markup'),
    
    # Collection markup and annotation (users)
    url(r'^collections/(?P<cid>\d+)/text/markup$',views.collection_markup_text,name='collection_markup_text'),
    url(r'^collections/(?P<cid>\d+)/text/describe$',views.collection_describe_text,name='collection_describe_text'),
    url(r'^collections/(?P<cid>\d+)/text/annotate$',views.collection_annotate_text,name='collection_annotate_text'),
    url(r'^collections/(?P<cid>\d+)/entity/(?P<uid>\d+)/text/describe$',views.describe_text,name='describe_text'),
    url(r'^collections/(?P<cid>\d+)/text/(?P<uid>.+?)/markup$',views.markup_text,name='markup_text'),

    # Flag Images and Text
    url(r'^actions/images/(?P<uid>.+?)/flag$',actions.flag_image,name='flag_image'),
    url(r'^actions/text/(?P<uid>.+?)/flag$',actions.flag_text,name='flag_text'),

    ## TEAM annotation
    url(r'^teams/(?P<tid>\d+)/collection/(?P<cid>\d+)/text/markup$',views.collection_markup_text,name='collection_markup_text'),
    url(r'^teams/(?P<tid>\d+)/collection/(?P<cid>\d+)/text/describe$',views.collection_describe_text,name='collection_describe_text'),
    url(r'^teams/(?P<tid>\d+)/collection/(?P<cid>\d+)/text/annotate$',views.collection_annotate_text,name='collection_annotate_text'),
    url(r'^teams/(?P<tid>\d+)/collection/(?P<cid>\d+)/entity/(?P<uid>\d+)/text/describe$',views.describe_text,name='describe_text'),
    url(r'^teams/(?P<tid>\d+)/collection/(?P<cid>\d+)/text/(?P<uid>.+?)/markup$',views.markup_text,name='markup_text'),
    url(r'^teams/(?P<tid>\d+)/collection/(?P<cid>\d+)/images/markup$',views.collection_markup_image,name='collection_markup_image'),
    url(r'^teams/(?P<tid>\d+)/collection/(?P<cid>\d+)/images/describe$',views.collection_describe_image,name='collection_describe_image'),
    url(r'^teams/(?P<tid>\d+)/collection/(?P<cid>\d+)/images/(?P<uid>.+?)/markup$',views.markup_image,name='markup_image'),
    url(r'^teams/(?P<tid>\d+)/collection/(?P<cid>\d+)/images/(?P<uid>\d+)/describe$',views.describe_image,name='describe_image'),
    url(r'^teams/(?P<tid>\d+)/collection/(?P<cid>\d+)/images/annotate$',views.collection_annotate_image,name='collection_annotate_image'),

]
