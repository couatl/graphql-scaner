import pandas as pd

from public.schema import Schema


def get_full_type(t, modifiers=None):
    if modifiers is None:
        modifiers = []
    if t['kind'] in ['NON_NULL', 'LIST']:
        return get_full_type(t['ofType'], modifiers + [t['kind']])
    return t['name'], modifiers


# Вершины графа - [идентификатор, имя типа] - все типы в схеме
# Рёбра графа:
# - идентификатор вершины
# - ребенок
# - модификаторы ребер (имя для запроса, NON_NULL, LIST)
#
# При обходе будет такая структура:
# - идентификатор 1 вершины
# - идентификатор 2 вершины
# - идентификатор 3 вершины
# ...
# - модификаторы 1-2
# - модификаторы 2-3 и т.д.
class Graph:
    def __init__(self, schema: Schema):
        self.schema = schema

    def build_graph(self):
        schema = self.schema.get_schema()
        types = schema['data']['__schema']['types']
        vertexes = []
        edges = []

        for i, t in enumerate(types):
            name = t['name']
            vertexes.append([i, name])

        # Вершины храним как data frame для удобства работы
        vertexes = pd.DataFrame.from_records(vertexes, columns=['id', 'name'])

        for i, t in enumerate(types):
            if ('fields' in t) and (t['fields'] is not None):
                for f in t['fields']:
                    child_name, modifiers = get_full_type(f['type'])
                    edges.append(
                        [i, vertexes[vertexes.name == child_name].id.values[0], f['name'], 'NON_NULL' in modifiers,
                         'LIST' in modifiers])
        edges = pd.DataFrame.from_records(edges, columns=['id_from', 'id_to', 'arg_name', 'NON_NULL', 'LIST'])

        return vertexes, edges


class CyclesDetector:
    def __init__(self, schema: Schema):
        self.schema = schema
        self.graph = None

    def detect(self):
        self.schema.get_schema()
        self.graph = Graph(self.schema).build_graph()

        loops = self.find_loops()
        loops_path = self.get_loops_queries(loops)

        return loops_path

    def get_loops_queries(self, loops, loop_depth=3):
        print('Found %d loops' % len(loops))
        print('Showing first 5 loops: ')
        paths = []

        for loop in loops:
            loop_begin = loop.ids.index(loop.id_to)
            start_args = ['arg_name_%d_%d' % (i, i + 1) for i in range(loop_begin)]
            prolog_strs = list(loop[start_args].values)
            loop_args = ['arg_name_%d_%d' % (i, i + 1) for i in range(loop_begin, len(loop.ids) - 1)]
            loop_strs = list(loop[loop_args].values) + [loop.arg_name]
            path = '|'.join([loop.start_word] + prolog_strs + loop_strs * loop_depth)
            paths.append(path)

        return paths

    def check_loop_for_list(self, loop):
        loop_begin = loop.ids.index(loop.id_to)

        for i in range(loop_begin, len(loop.ids) - 1):
            if loop['LIST_%d_%d' % (i, i + 1)]:
                return True

        return False

    def find_loops(self):
        vertexes, edges = self.graph
        query_type, mutation_type = self.schema.get_query_and_mutation_types()

        if mutation_type is not None:
            types = [query_type, mutation_type]
        else:
            types = [query_type]

        loops_to_find = 10

        start = vertexes[vertexes.name.apply(lambda x: x in types)][['id']]
        start.columns = ['id_0']
        start['ids'] = start.id_0.apply(lambda x: [x])
        start['start_word'] = types
        move = 0
        current = start
        loops = []

        print('Starting finding loops in application...')

        while True:
            print('--- %d iteration' % (move + 1))
            result = current.merge(edges, left_on='id_%d' % move, right_on='id_from')

            if result.shape[0] == 0:
                break

            result.drop('id_from', axis=1, inplace=True)
            loops_recs = result.apply(lambda x: x.id_to in x.ids, axis=1)

            if loops_recs.any():
                print('    Loops found')

                for name, row in result[loops_recs].iterrows():
                    if self.check_loop_for_list(row):
                        loops.append(row)
                        if len(loops) >= loops_to_find:
                            return loops

                result.drop(result[loops_recs].index, inplace=True)

            result['ids'] = result.ids.apply(lambda x: x.copy())
            result.apply(lambda x: x.ids.append(x.id_to), axis=1)
            result.rename(columns={'id_to': 'id_%d' % (move + 1),
                                   'NON_NULL': 'NON_NULL_%d_%d' % (move, move + 1),
                                   'arg_name': 'arg_name_%d_%d' % (move, move + 1),
                                   'LIST': 'LIST_%d_%d' % (move, move + 1)}, inplace=True)

            current = result
            move += 1

        return loops
