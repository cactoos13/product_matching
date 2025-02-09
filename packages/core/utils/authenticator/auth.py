from streamlit_authenticator import Authenticate
import yaml
from yaml import SafeLoader


class Auth:
    def __init__(self):
        with open('./credentials.yml') as file:
            config = yaml.load(file, Loader=SafeLoader)
        self.config = config


    def get_roles(self, username: str):
        return self.config['credentials']['usernames'][username]['pages']
    def get_authenticator(self):
        return Authenticate(
            credentials=self.config['credentials'],
            cookie_name=self.config['cookie']['name'],
            cookie_key=self.config['cookie']['key'],
            cookie_expiry_days=self.config['cookie']['expiry_days']
        )
