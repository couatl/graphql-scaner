import os

from public.utils import QueryRunner


class BrokenAccessControlDetector:
    def __init__(self, query_runner: QueryRunner):
        self.query_runner = query_runner

    def detect(self):
        os.system('node introspectionToSchema.js')

        # TODO: передавать куки и заголовки
        os.system('node brokenAccessDetector.js %s' % self.query_runner.url)
