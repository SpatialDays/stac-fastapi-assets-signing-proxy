from abc import abstractmethod

class SigningMiddleware:

    def __init__(self):
        pass
    
    def sign_all_assets(self,data):
        def change_href(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == "href":
                        data[key] = self.sign_href(value)
                    else:
                        change_href(value)
            elif isinstance(data, list):
                for item in data:
                    change_href(item)
            return data

        # Call change_href with a new value for the href keys
        new_data = change_href(data)
        # Print the modified JSON data
        return new_data
    

    @abstractmethod
    def sign_href(self, href):
        pass