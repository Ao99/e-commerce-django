from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Set port for localhost'
    
    def add_arguments(self, parser):
        parser.add_argument('current_port', type=str, nargs='+',
                            help='The current port for localhost')
        parser.add_argument('new_port', type=str, nargs='+',
                            help='The new port for localhost')
        
    def handle(self, *args, **kwargs):
        current_port = kwargs['current_port'][0]
        current = f"default_port = '{current_port}'"
        new_port = kwargs['new_port'][0]
        new = f"default_port = '{new_port}'"
        f = '../env/lib/python3.6/site-packages/django/core/management/commands/runserver.py'
        
        with open(f, 'r') as file:
            filedata = file.read()
        
        changed = False
        for line in filedata:
            if current in line:        
                filedata = filedata.replace(current, new)
                with open(f, 'w') as file:
                    file.write(filedata)
                self.stdout.write(self.style.SUCCESS('Port for localhost has been changed to %s' % new_port))
                changed = True
                break
        if not changed:
            self.stdout.write(self.style.ERROR('Error: port for localhost has not been changed, incorrect current port: %s' % current_port))