import sys
import argparse

from public.cycles import CyclesDetector
from public.utils import QueryRunner
from public.schema import Schema


def parse_args(args):
    parser = argparse.ArgumentParser(description='Async File Storage')
    parser.add_argument(
        '-u', '--url',
        help='GraphQL endpoint url'
    )
    parser.add_argument(
        '-c', '--cookie',
        help='Authorization cookie'
    )
    parser.add_argument(
        '--header',
        help='HTTP headers',
        action='append'
    )
    return parser.parse_args(args)


def print_cycles(cycles):
    if len(cycles):
        print('\n'.join(cycles))


def main():
    params = parse_args(sys.argv[1:])

    if params.url is None:
        print("You need to provide GraphQL endpoint url (-u)")
        exit(1)

    query_runner = QueryRunner(params.url, params.cookie, params.header)
    schema = Schema(query_runner)

    # Циклические зависимости в схеме
    cycles = CyclesDetector(schema).detect()
    # queries = BrokenAccessControlDetector(query_runner).detect()


if __name__ == '__main__':
    main()
