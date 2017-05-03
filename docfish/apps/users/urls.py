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

from django.conf.urls import url, include
from django.conf import settings
from docfish.apps.users import views as user_views
from social_django import urls as social_urls

urlpatterns = [

    # Twitter, and social auth
    url(r'^login/$', user_views.login, name="login"),
    url(r'^accounts/login/$', user_views.login, name="login"),
    url(r'^home/$', user_views.login),
    url(r'^logout/$', user_views.logout, name="logout"),
    url('', include(social_urls, namespace='social')),

    # Teams
    url(r'^teams$', user_views.view_teams, name="teams"),
    url(r'^users$', user_views.view_users, name="users"),
    url(r'^teams/(?P<tid>.+?)/view$', user_views.view_team, name="team_details"),
    url(r'^teams/(?P<tid>.+?)/edit$', user_views.edit_team, name="edit_team"),
    url(r'^teams/(?P<tid>.+?)/join$', user_views.join_team, name="join_team"),
    url(r'^teams/(?P<tid>.+?)/request/join$', user_views.request_membership, name="request_join_team"),
    url(r'^teams/new$',user_views.edit_team,name='new_team'),
    url(r'^teams/new$',user_views.edit_team,name='new_team'),

]
