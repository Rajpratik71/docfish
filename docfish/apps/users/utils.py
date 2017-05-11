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

from django.contrib.auth.models import User
from django.http.response import (
    HttpResponseRedirect, 
    HttpResponseForbidden, 
    Http404
)
from django.shortcuts import (
    get_object_or_404, 
    render_to_response, 
    render, 
    redirect
)
from django.conf import settings
from django.contrib.auth import get_user_model
from docfish.apps.main.models import *
import collections
from datetime import datetime
from datetime import timedelta
from itertools import chain
from numpy import unique
import operator
import os

from django.utils import timezone

from docfish.apps.users.models import Team

def get_user(uid):
    '''get a single user, or return 404'''
    keyargs = {'id':uid}
    try:
        user = User.objects.get(**keyargs)
    except User.DoesNotExist:
        raise Http404
    else:
        return user


def get_team(tid,return_none=False):
    '''get a single team, or return 404'''
    keyargs = {'id':tid}
    try:
        team = Team.objects.get(**keyargs)
    except Team.DoesNotExist:
        if return_none:
            return None
        raise Http404
    else:
        return team


def get_invite(team,code):
    keyargs = {'team':code,
               'team':team}
    try:
        invite = MembershipInvite.objects.get(**keyargs)
    except MembershipRequest.DoesNotExist:
        return None
    else:
        return invite


def get_request(team,user):
    keyargs = {'user':user,
               'team':team}
    try:
        req = MembershipRequest.objects.get(**keyargs)
    except MembershipRequest.DoesNotExist:
        return None
    else:
        return req


####################################################################################
# SUMMARY FUNCTIONS ################################################################
####################################################################################



def summarize_team_annotations(members):
    '''summarize_team_annotations will return a summary of annotations for a group of users, typically a team
    :param members: a list or queryset of users
    '''
    counts = dict()
    total = 0
    for member in members:
        member_counts = count_user_annotations(member)
        member_count = sum(member_counts.values())
        counts[member.username] = member_count
        total += member_count
    counts['total'] = total
    return counts    


def count_user_annotations(users):
    '''return the count of a single user's annotations, by type
    (meaning across images, text, annotations, descriptions, and markups)
    '''
    counts = dict()

    # Count for a single user
    if isinstance(users,User):
        counts['image-markup'] = ImageMarkup.objects.filter(creator=users).distinct().count()
        counts['text-markup'] = TextMarkup.objects.filter(creator=users).distinct().count()
        counts['text-annotation'] = TextAnnotation.objects.filter(creator=users).distinct().count()
        counts['image-annotation'] = ImageAnnotation.objects.filter(creator=users).distinct().count()
        counts['text-description'] = TextDescription.objects.filter(creator=users).distinct().count()
        counts['image-description'] = ImageDescription.objects.filter(creator=users).distinct().count()

    # or count across a group of users
    else:
        counts['image-markup'] = ImageMarkup.objects.filter(creator__in=users).distinct().count()
        counts['text-markup'] = TextMarkup.objects.filter(creator__in=users).distinct().count()
        counts['text-annotation'] = TextAnnotation.objects.filter(creator__in=users).distinct().count()
        counts['image-annotation'] = ImageAnnotation.objects.filter(creator__in=users).distinct().count()
        counts['text-description'] = TextDescription.objects.filter(creator__in=users).distinct().count()
        counts['image-description'] = ImageDescription.objects.filter(creator__in=users).distinct().count()

    return counts


def count_team_annotations(team):
    '''return the count of a single user's annotations, by type
    (meaning across images, text, annotations, descriptions, and markups)
    '''
    counts = dict()

    counts['image-markup'] = ImageMarkup.objects.filter(team=team).distinct().count()
    counts['text-markup'] = TextMarkup.objects.filter(team=team).distinct().count()
    counts['text-annotation'] = TextAnnotation.objects.filter(team=team).distinct().count()
    counts['image-annotation'] = ImageAnnotation.objects.filter(team=team).distinct().count()
    counts['text-description'] = TextDescription.objects.filter(team=team).distinct().count()
    counts['image-description'] = ImageDescription.objects.filter(team=team).distinct().count()

    return counts


def count_annotations_bydate(user):
    '''return a list of dates and counts that a user has annotated, in the past year.
    '''
    dates = dict()
    now = timezone.now()
    then = now + timezone.timedelta(days=-365)

    # For each, get all annotation objects
    annots = []
    annots = chain(annots,ImageMarkup.objects.filter(creator=user).distinct())
    annots = chain(annots,TextMarkup.objects.filter(creator=user).distinct())
    annots = chain(annots,TextAnnotation.objects.filter(creator=user).distinct())
    annots = chain(annots,ImageAnnotation.objects.filter(creator=user).distinct())
    annots = chain(annots,TextDescription.objects.filter(creator=user).distinct())
    annots = chain(annots,ImageDescription.objects.filter(creator=user).distinct())
    annots = list(annots)
    for annot in annots:
        annotation_time = annot.modify_date
        annotation_time = annotation_time.replace(hour=0, minute=0, second=0, microsecond=0)
        if annotation_time > then and annotation_time < now:
            if annotation_time not in dates:
                dates[annotation_time] = 1
            else:
                dates[annotation_time] +=1
    return dates


def summarize_teams_annotations(teams,sort=True):
    '''summarize_teams_annotations returns a sorted list with [(team:count)] 
    :param members: a list or queryset of users
    :param sort: sort the result (default is True)
    '''
    sorted_teams = dict()
    for team in teams:
        team_count = summarize_team_annotations(team.members.all())['total']
        sorted_teams[team.id] = team_count
    if sort == True:
        sorted_teams = sorted(sorted_teams.items(), key=operator.itemgetter(1))
        sorted_teams.reverse() # ensure returns from most to least
    return sorted_teams



####################################################################################
# TEAM FUNCTIONS ###################################################################
####################################################################################


def get_user_team(request):
    ''' get the team of the authenticated user
    '''
    if request.user.is_authenticated():
        user_team = Team.objects.filter(members=request.user)
        if len(user_team) > 0:
            return user_team[0]
    return None


def is_invite_valid(team,code):
    '''determine if a user can be added to a team meaning
    he or she has an invite, and the invite corresponds to the
    code generated for it. a status (True or False)
    '''
    invitation = get_invite(team,code)
    if invitation is None:
        return False
    if invitation.code == code:
        return True
    return False


def add_user(user,team,code=None):
    '''add a user to a team. If a code is provided,
    the invitation object is deleted.
    '''
    if code is not None:
        invitation = get_invite(team,code)
        if invitation is not None:
            invitation.delete()

        # Update the user request, if provided
        user_request = get_request(team,user)
        if user_request is not None:
            user_request.status = "GRANTED"
            user_request.save()

    # Finally, add the user
    team.members.add(user)
    team.save()
    return team


def has_team_edit_permission(request,team):
    '''only the owner of a team can edit it.
    '''
    if request.user == team.owner:
        return True
    return False


def has_same_institution(owner,requester):
    '''a general function to determine if two users belong to
    the same institution, based on SAML. This only works if the user
    account is logged in with SAML
    '''

    # Does the user have an institution login?
    user_providers = [sa for sa in requester.social_auth.all() if sa.provider == 'saml']
    if len(user_providers) == 0:
        return False

    # Limit to those in user's institution
    user_institutions = [sa.uid.split(':')[0] for sa in user_providers]
    owner_institutions = [sa.uid.split(':')[0] for sa in owner.social_auth.all()]
    shared_institution = set(user_institutions).intersection(set(owner_institutions))

    if len(shared_institution) > 0:
        return True
    return False



def has_saml(user):
    '''return true if the user has some account with SAML
    '''
    # Does the user have an institution login?
    user_providers = [sa for sa in user.social_auth.all() if sa.provider == 'saml']
    if len(user_providers) == 0:
        return False
    return True


####################################################################################
# TEAM VIEWS #######################################################################
####################################################################################

# Markups --------------------------------------------------------------------------
def get_team_markups(team,get_images=True):
    if get_images == True:
        return get_image_markups(team)
    return get_text_markups(team)

def get_image_markups(team):
    return ImageMarkup.objects.filter(team=team)

def get_text_markups(teams):
    return TextMarkup.object.filter(team=team)


# Descriptions ----------------------------------------------------------------------
def get_team_descriptions(team,get_images=True):
    if get_images == True:
        return get_image_descriptions(team)
    return get_text_descriptions(team)

def get_image_descriptions(team):
    return ImageDescription.objects.filter(team=team)

def get_text_descriptions(team):
    return TextDescription.objects.filter(team=team)


# Annotations -----------------------------------------------------------------------
def get_team_annotations(team,get_images=True):
    if get_images == True:
        return get_image_annotations(team)
    return get_text_annotations(team)

def get_image_annotations(team):
    return ImageAnnoatation.objects.filter(team=team)

def get_text_annotations(team):
    return TextAnnotation.objects.filter(team=team)
