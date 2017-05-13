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

from django.core import serializers
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, render
from django.template.context import RequestContext

import logging
import os
import pickle
import uuid

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse,
    JsonResponse, 
    HttpResponseBadRequest, 
    HttpResponseRedirect
)

from docfish.apps.snacks.models import SnackBox
from docfish.apps.users.forms import TeamForm
from docfish.apps.users.models import *
from docfish.apps.users.utils import *


##################################################################################
# AUTHENTICATION VIEWS ###########################################################
##################################################################################

def login(request):
    #context = {'request': request, 'user': request.user}
    #context = RequestContext(request,context)
    #return render_to_response('social/login.html', context_instance=context)
    if request.user.is_authenticated():
        return redirect('collection_chooser')
    return render(request,'social/login.html')


@login_required(login_url='/')
def home(request):
    return render_to_response('social/home.html')


def logout(request):
    '''log out of the social authentication backend'''
    auth_logout(request)
    return redirect('/')


##################################################################################
# TEAM VIEWS #####################################################################
##################################################################################


@login_required
def edit_team(request, tid=None):
    '''edit_team is the view to edit an existing team, or create a new team.
    :parma tid: the team id to edit or create. If none, indicates a new team
    '''
    if tid:
        team = get_team(tid)
        edit_permission = has_team_edit_permission(request,team)
        title = "Edit Team"
    else:
        team = Team(owner=request.user)
        edit_permission = True
        title = "New Team"

    # Only the owner is allowed to edit a team
    if edit_permission:

        if request.method == "POST":
            form = TeamForm(request.POST,request.FILES,instance=team)
            if form.is_valid():
                team = form.save(commit=False)
                team.save()
                # The team can only be institution given that the user has SAML
                if team.permission == "institution":
                    if not has_saml(team.owner):
                        team.permission = "invite"
                        messages.info(request,'''Institution invitation requires you to login with SAML.
                                                 Your team has been created with an "invite only" permission.''')
                team.members.add(request.user)
                team.save()
                return HttpResponseRedirect(team.get_absolute_url())
        else:
            form = TeamForm(instance=team)

        context = {"form": form,
                   "edit_permission": edit_permission,
                   "title":title,
                   "team":team}

        return render(request, "teams/edit_team.html", context)

    # If user makes it down here, does not have permission
    messages.info(request, "Only team owners can edit teams.")
    return redirect("teams")


def view_teams(request):
    '''view all teams (log in not required)
    :parma tid: the team id to edit or create. If none, indicates a new team
    '''
    teams = Team.objects.all()
    context = {"teams": teams}
    user_team = get_user_team(request)
    context['user_team'] = user_team # returns None if not in team

    return render(request, "teams/all_teams.html", context)


def view_users(request):
    '''view all users
    '''
    users = User.objects.all()
    counts = summarize_member_annotations(users)
    lookups = []
    for user in users:
        if user.username != "AnonymousUser":
            userinfo = {'teams': user.team_set.all(),
                        'count':counts[user.username],
                        'name':user.username,
                        'id':user.id,
                        'snacks':SnackBox.objects.filter(user=user).first()}
            lookups.append(userinfo)

    context = {"users": lookups}
    return render(request, "users/all_users.html", context)


@login_required
def view_team(request, tid, code=None):
    '''view the details about a team
    :parma tid: the team id to edit or create. If none, indicates a new team
    '''
    team = get_team(tid)

    # Need to create annotation counts with "total" for all members
    annotation_counts = summarize_member_annotations(team.members.all())
    edit_permission = has_team_edit_permission(request,team)

    context = {"team": team,
               "edit_permission":edit_permission,
               "annotation_counts":annotation_counts}

    # If the user has generated an invitation code
    if code is not None:
        context['code'] = code

    return render(request, "teams/team_details.html", context)


##################################################################################
# TEAM REQUESTS ##################################################################
##################################################################################


@login_required
def join_team(request, tid, code=None):
    '''add a user to a new team, and remove from previous team
    :parma tid: the team id to edit or create. If none, indicates a new team
    :param code: if the user is accessing an invite link, the code is checked
    against the generated request.
    '''
    team = get_team(tid)
    user = request.user
    add_user = True

    if team.permission == "institution":
        if not has_same_institution(request.user,team.owner):
            add_user = False
            # A user can be invited from a different institution
            if code is not None:
                add_user = is_invite_valid(team, code)
                if add_user == False:
                    messages.info(request, "You are not from the same institution, and this code is invalid to join.")
            else:
                messages.info(request,'''This team is only open to users in the team owner's institution.
                                         If you have an email associated with the institution, use the SAML institution
                                         log in.''')
            
    elif team.permission == "invite":
        if code is None:
            messages.info(request,"This is not a valid invitation to join this team.")
            add_user = False
        else:    
            add_user = is_invite_valid(team, code)
            if add_user == False:
                messages.info(request, "This code is invalid to join this team.")

    if add_user:   
        if user not in team.members.all():
            team.members.add(user)
            team.save()
            messages.info(request,"You have been added to team %s" %(team.name))
        else:
            messages.info(request,"You are already a member of %s!" %(team.name))

    return HttpResponseRedirect(team.get_absolute_url())


def add_collections(request,tid):
    team = get_team(tid)
    if request.method == "POST":
        if request.user == team.owner:
            collection_ids = request.POST.getlist("collection_ids",None)
            if collection_ids is not None:
                for collection_id in collection_ids:
                    team.add_collection(collection_id)
                team.save()
                messages.info(request,"%s collections added to team!" %(len(collection_ids)))
        else:
            messages.info(request, "Only team owners can edit teams.")
            return HttpResponseRedirect(team.get_absolute_url())

    context = {"team": team}
    return render(request, "teams/add_team_collections.html", context)


##################################################################################
# TEAM ACTIONS ###################################################################
##################################################################################

# Membership

@login_required
def request_membership(request,tid):
    '''generate an invitation for a user, return to view
    '''
    team = get_team(tid)
    if request.user not in team.members.all():
        old_request = get_request(user=request.user,team=team)
        if old_request is not None:
            message = "You already have a request to join team %s with status %s" %(team.name,
                                                                                    old_request.status)
        else:
            new_request = MembershipRequest.objects.create(team=team,
                                                           user=request.user)
            new_request.save()
            message = "Your request to join %s has been submit." %(team.name)

    else:
        message = "You are already a member of this team."
    return JsonResponse({"message":message})


@login_required
def leave_team(request,tid):
    team = get_team(tid)
    if request.user in team.members.all():
        team.members.remove(member)
        team.save()        
        message = "You has been removed from %s" %(team.name)
    else:
        message = "You are not a part of %s" %(team.name)
    return redirect('teams')


@login_required
def remove_member(request,tid,uid):
    team = get_team(tid)
    member = get_user(uid)
    if request.user == team.owner:
        if member in team.members.all():
            team.members.remove(member)
            team.save()        
            message = "%s has been removed from the team" %member.username
        else:
            message = "%s is not a part of this team." %member.username
    else:
        message = "You are not allowed to perform this action."
    return JsonResponse({"message":message})


@login_required
def generate_team_invite(request,tid):
    '''generate an invitation for a user, return to view
    '''
    team = get_team(tid)
    if request.user == team.owner:
        code = uuid.uuid4()
        new_invite = MembershipInvite.objects.create(team=team,
                                                     code=code)
        new_invite.save()
        return view_team(request, team.id, code=code)

    messages.info(request,"You do not have permission to invite to this team.")
    return HttpResponseRedirect(team.get_absolute_url())


# Collections

def remove_collection(request,tid,cid):
    team = get_team(tid)
    if request.user == team.owner:
        team.remove_collection(cid)    
        message = "Collection successfully removed."
    else:
        message = "You are not allowed to perform this action."
    return JsonResponse({"message":message})



# Python social auth extensions

def redirect_if_no_refresh_token(backend, response, social, *args, **kwargs):
    '''http://python-social-auth.readthedocs.io/en/latest/use_cases.html
       #re-prompt-google-oauth2-users-to-refresh-the-refresh-token
    '''
    if backend.name == 'google-oauth2' and social and response.get('refresh_token') is None and social.extra_data.get('refresh_token') is None:
        return redirect('/login/google-oauth2?approval_prompt=force')


# A User should not be allowed to associate a Github (or other) account with a different
# gmail, etc.
def social_user(backend, uid, user=None, *args, **kwargs):
    '''OVERRIDED: It will give the user an error message if the
    account is already associated with a username.'''
    provider = backend.name
    social = backend.strategy.storage.user.get_social_auth(provider, uid)
    if social:
        if user and social.user != user:
            msg = 'This {0} account is already in use.'.format(provider)
            messages.info(backend.strategy.request,msg)
            return login(request=backend.strategy.request)
            #raise AuthAlreadyAssociated(backend, msg)
        elif not user:
            user = social.user

    return {'social': social,
            'user': user,
            'is_new': user is None,
            'new_association': social is None}

