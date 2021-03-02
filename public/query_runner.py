import requests


class QueryRunner:
    cookies = None
    url = None
    headers = None

    @staticmethod
    def run_query(query):
        url = QueryRunner.url

        if url is None:
            raise Exception('You need to define GraphQL endpoint url')

        request = requests.post(url, json=query, verify=False, cookies=QueryRunner.cookies, headers=QueryRunner.headers)

        if request.status_code == 200:
            return request.json()
        else:
            return None
