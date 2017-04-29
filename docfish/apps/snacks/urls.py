from django.conf.urls import url, include
from django.conf import settings
from docfish.apps.snacks import views as snack_views

urlpatterns = [

    url(r'^snacks/$', snack_views.snacks_home, name="snacks"),
    url(r'^snacks/my$', snack_views.view_snacks, name="my_snacks"),
    url(r'^snacks/(?P<sid>\d+)/details$', snack_views.snack_details, name="snack_details"),
    url(r'^snacks/category/(?P<cid>\d+)$', snack_views.snack_category, name="snack_category"),
    url(r'^snacks/category/(?P<cid>\d+)/(?P<page>\d+)$', snack_views.snack_category, name="snack_category"),
    url(r'^snacks/all$', snack_views.all_snacks, name="all_snacks"),
    url(r'^snacks/all/(?P<page>\d+)$', snack_views.all_snacks, name="all_snacks"),

    # User snack options
    url(r'^snacks/add/(?P<sid>\d+)$', snack_views.add_snack, name="add_snack"),
    url(r'^snacks/remove/(?P<sid>\d+)$', snack_views.remove_snack, name="remove_snack"),
    url(r'^snacks/disable/(?P<sid>\d+)$', snack_views.disable_snack, name="disable_snack"),
    url(r'^snacks/enable/(?P<sid>\d+)$', snack_views.enable_snack, name="enable_snack"),
    url(r'^snacks/redeem$', snack_views.redeem_snacks, name="redeem_snacks"),
    
    # Snack search
    url(r'^snacks/search$', snack_views.search_view, name="search"),
    url(r'^snacks/searching$', snack_views.snack_search, name="snack_search"),

    # User snacks
    url(r'^users/snacks/(?P<uid>\d+)$', snack_views.user_snacks, name="user_snacks"),

]
