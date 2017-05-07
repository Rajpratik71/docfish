'''

permissions functions

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

from docfish.apps.users.utils import has_same_institution
from django.contrib.auth.decorators import login_required


###############################################################################################
# Authentication and Collection View Permissions###############################################
###############################################################################################


@login_required
def get_permissions(request,context):
    '''get_permissions returns an updated context with edit_permission and annotate_permission
    for a user. The key "collection" must be in the context
    '''
    collection = context["collection"]

    # Edit and annotate permissions?
    context["edit_permission"] = has_collection_edit_permission(request,collection)
    context["delete_permission"] = request.user == collection.owner
    
    return context


# Does a user have permissions to see a collection?

def has_delete_permission(request,collection):
    '''collection owners have delete permission'''
    if request.user == collection.owner:
        return True
    return False


def has_collection_edit_permission(request,collection):
    '''owners and contributors have edit permission'''
    if request.user == collection.owner or request.user in collection.contributors.all():
        return True
    return False


# Supporting function
def has_collection_annotate_permission(request,collection):
    '''owner and annotators have annotate permission (not contributors)'''
    from docfish.apps.users.models import Team
    if request.user == collection.owner:
        return True
    return has_same_institution(owner=request.user,
                                requester=collection.owner)


