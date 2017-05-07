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

urlpatterns = [

    # Change / add contributors
    url(r'^contributors/(?P<cid>\d+)/(?P<uid>.+?)/remove$',views.remove_contributor,name='remove_contributor'),
    url(r'^contributors/(?P<cid>\d+)/add$',views.add_contributor,name='add_contributor'),
    url(r'^contributors/(?P<cid>\d+)/edit$',views.edit_contributors,name='edit_contributors'),

    # Video
    #url(r'^teams/video/describe$',views.video_describe_web,name='video_describe_web'),

]
