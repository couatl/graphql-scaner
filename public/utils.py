import requests


def get_splitted_value(value):
    if value is None:
        return value

    result = {}

    for i in value:
        splits = i.split('=', 1)
        if len(splits) == 1:
            result[splits[0]] = ''
        else:
            result[splits[0]] = splits[1]

    return result


class QueryRunner:
    def __init__(self, url, cookies=None, headers=None):
        self.url = url
        self.cookies = get_splitted_value(cookies)
        self.headers = get_splitted_value(headers)

    def run_query(self, query):
        url = self.url
        cookies = self.cookies
        headers = self.headers

        if url is None:
            raise Exception('You need to define GraphQL endpoint url')

        print(url, query)
        request = requests.post(url, json=query, verify=False, cookies=cookies, headers=headers)

        if request.status_code == 200:
            return request.json()
        else:
            return request.json()
