import requests

class Search:
    def __init__(self, url_prefix):
        self.url_prefix = url_prefix
    
    def search(self, parameters, page, result_per_page) -> int:
        json = {
            "parameters": parameters,
            "page": page,
            "result_per_page": result_per_page
        }
        url = self.url_prefix
        r = requests.post(url, json=json)
        response_json = r.json()
        return r.status_code, response_json.get("results")