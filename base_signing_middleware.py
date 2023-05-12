from abc import abstractmethod

class SigningMiddleware:

    def __init__(self):
        pass
    
    def sign_all_assets(self, data):
        def change_href(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == "href":
                        data[key] = self.sign_href(value)
                    elif key == "links":
                        continue  # skip processing "links" key
                    else:
                        change_href(value)
            elif isinstance(data, list):
                for item in data:
                    change_href(item)
            return data

        new_data = change_href(data)
        return new_data
    

    @abstractmethod
    def sign_href(self, href):
        pass