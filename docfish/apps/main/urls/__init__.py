from .collections import urlpatterns as collection_urls
from .markup import urlpatterns as markup_urls
from .annotate import urlpatterns as annotate_urls
from .entity import urlpatterns as entity_urls
from .describe import urlpatterns as describe_urls
from .collaborate import urlpatterns as team_urls

urlpatterns = collection_urls + markup_urls + annotate_urls + entity_urls + describe_urls + team_urls
