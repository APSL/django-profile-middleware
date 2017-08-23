
from __future__ import with_statement

import pstats
from django.conf import settings
import cProfile
from io import StringIO


class ProfilerMiddleware(object):

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response

    def can(self, request):
        if settings.DEBUG and settings.PROFILER["enable"]:
            return True

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if self.can(request):
            self.profiler = cProfile.Profile()
            self.profiler.enable()

    def process_response(self, request, response):
        if self.can(request):
            self.profiler.disable()

            s = StringIO()

            sortby = settings.PROFILER.get('sort', 'time')
            count = settings.PROFILER.get('count', None)

            pstats.Stats(self.profiler, stream=s).sort_stats(sortby).print_stats(count)

            for output in settings.PROFILER.get('output', ['console',  'file']):

                if output == 'console':
                    print(s.getvalue())

                if output == 'file':
                    file_loc = settings.PROFILER.get('file_location', 'profiling_results.txt')
                    with open(file_loc, 'a+') as file:
                        counter = str(s.getvalue())
                        file.write(counter)

        return response
