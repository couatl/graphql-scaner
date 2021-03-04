import json

from public.utils import QueryRunner


class Schema:
    def __init__(self, query_runner: QueryRunner):
        self.query_runner = query_runner
        self.schema = None

    def get_schema(self):
        if self.schema is not None:
            return self.schema

        try:
            with open('graphql/schema.json', 'rt') as f:
                schema = json.loads(f.read())
                self.schema = schema

                return schema
        except:
            pass

        with open('graphql/IntrospectionQuery.json', 'rt') as f:
            introspection_query = f.read()

        schema = self.query_runner.run_query(json.loads(introspection_query))

        with open('graphql/schema.json', 'wt') as f:
            json.dump(schema, f)

        self.schema = schema

        return schema

    def get_query_and_mutation_types(self):
        query_type = None
        mutation_type = None

        if self.schema is None:
            self.get_schema()

        schema = self.schema

        if schema['data']['__schema']['queryType'] is not None:
            query_type = schema['data']['__schema']['queryType']['name']
        if schema['data']['__schema']['mutationType'] is not None:
            mutation_type = schema['data']['__schema']['mutationType']['name']

        return query_type, mutation_type
