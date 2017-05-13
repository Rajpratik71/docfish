from django.core.management.base import (
    NoArgsCommand,
    BaseCommand
)
from docfish.apps.users.tasks import update_team_rankings

class Command(BaseCommand):
    '''This command will update team rankings once a day
    it is scheduled via a system cron job (once a day)
    '''
    help = "Updates team rankings"
    def handle(self,*args, **options):
        update_team_rankings()
