import os
import re

from public.schema import Schema
from public.utils import QueryRunner

# Note: Date and DateTime are not graphQL scpecified. It is typical scalars, but format could be different
default_table = {'String': ['"test_string"'],
                 'ID': ['1', '"5ed496cc-c971-11dc-93cd-15767af24309"'],
                 'Int': ['1'],
                 'DateTime': ['"2017-07-09T11:54:42"'],
                 'Date': ['"2017-07-09"'],
                 'Float': ['3.1415'],
                 'Boolean': ['true'],
                 'URI': ['"http://example.com/"']}

placehoder_table = {'String': '|String|',
                    'ID': '|ID|',
                    'Int': '|Int|',
                    'DateTime': '|DateTime|',
                    'Date': '|Date|',
                    'Float': '|Float|',
                    'Boolean': '|Boolean|',
                    'URI': '|URI|'}


def get_gql_files(datalist, prefix):
    return [(prefix + '/' + val) for val in datalist if re.search(r'gql$', val)]


def apply_re_sub_for_strings(strings, pattern, replaces):
    res = []
    for s in strings:
        for r in replaces:
            res.append(re.sub(pattern, r, s))
    return res


class BrokenAccessControlDetector:
    def __init__(self, query_runner: QueryRunner):
        self.query_runner = query_runner

    def detect(self):
        queries_path = 'graphql/queries_output/queries'
        mutations_path = 'graphql/queries_output/mutations'

        files = []

        if os.path.isdir(queries_path):
            files += get_gql_files(os.listdir(queries_path), queries_path)

        if os.path.isdir(mutations_path):
            files += get_gql_files(os.listdir(mutations_path), mutations_path)

        if not len(files):
            print('No queries found')

            return

        for file in files:
            data = open(file).read()

            first_line = data.split('\n')[0]
            variables_s = re.findall('(\$[^:]*):\s([^,\)]*)', first_line)

            var_types = {}
            for x in variables_s:
                var_types[x[0]] = x[1]

            request_type = re.findall('^[^\ ]*', data)[0]
            # module = re.findall('\n\ {4}([^\ \n]*)\{', data)[0]
            functions = re.findall('(\ {8}[^\n]*\{[^\}]*})', data)

            new_query_tmpl = 'query{\n' + data.split('\n')[1] + '''
            %s    
                }
            }'''

            cur_funcs = []

            for f in functions:
                cur_funcs = [f]

                function_vars = re.findall('(\$[^,\)]*)', f)

                try:
                    for v in function_vars:
                        t = var_types[v]

                        if t[-1] != '!':  # Если опциональный аргумент - не указываем
                            cur_funcs = apply_re_sub_for_strings(
                                cur_funcs,
                                ',?\\s?[^\(,]*\\%s(,?\)?)' % v,
                                ['\\1']
                            )

                            continue

                        t = t[:-1]

                        if t not in default_table:
                            raise Exception('No default value for type: %s' % t)

                        else:  # Вставляем дефолтное значение
                            cur_funcs = apply_re_sub_for_strings(
                                cur_funcs,
                                '(,?\\s?[^\(,]*)\\%s(,?\)?)' % v
                                , ['\\1%s\\2' % x for x in default_table[t]]
                            )

                    cur_funcs = apply_re_sub_for_strings(
                        cur_funcs,
                        '(\(\))',
                        ['']
                    )

                except Exception as error:
                    print(str(error))

                    continue

            print(cur_funcs)

            for cur_func in cur_funcs:
                json_request = {'operationName': "",
                                'variables': {},
                                'query': new_query_tmpl % (cur_func)}

                result = self.query_runner.run_query(json_request)
                print(result)


            return
