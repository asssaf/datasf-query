import requests

class APIClient:
    def __init__(self, base_url, verify=True):
        self.base_url = base_url.rstrip('/')
        self.verify = verify

    def get(self, endpoint, params=None, headers=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.get(url, params=params, headers=headers, verify=self.verify)
            return response
        except requests.RequestException as e:
            # Handle generic request exceptions
            raise e
