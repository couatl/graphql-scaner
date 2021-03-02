import json

from public.query_runner import QueryRunner


def get_schema():
    with open('graphql/IntrospectionQuery.graphql', 'rt') as f:
        introspection_query = f.read()

    return QueryRunner.run_query(json.loads(introspection_query))
