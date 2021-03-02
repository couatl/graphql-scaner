import sys
import argparse

from public.query_runner import QueryRunner


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
        '-h', '--header',
        help='HTTP headers',
        action='append'
    )
    return parser.parse_args(args)


def main():
    params = parse_args(sys.argv[1:])

    if params.url is None:
        print("You need to provide GraphQL endpoint url (-u)")
        exit(1)

    QueryRunner.url = params.url

    if params.cookie is not None:
        cookie_dir = {}
        for cookie in params.cookie:
            splits = cookie.split('=', 1)
            if len(splits) == 1:
                cookie_dir[splits[0]] = ''
            else:
                cookie_dir[splits[0]] = splits[1]

        QueryRunner.cookies = cookie_dir

    if params.header is not None:
        header_dir = {}
        for header in params.header:
            splits = header.split('=', 1)
            if len(splits) == 1:
                header_dir[splits[0]] = ''
            else:
                header_dir[splits[0]] = splits[1]

        QueryRunner.headers = header_dir

    #  TODO


if __name__ == '__main__':
    main()
