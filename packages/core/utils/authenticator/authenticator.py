import functools
import streamlit as st
from packages.core.utils.authenticator import Auth



def authenticator(roles: list[str]):
    def check(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            auth = Auth().get_authenticator()
            if 'authentication_status' not in st.session_state:
                st.session_state['authentication_status'] = False

            if 'logout' not in st.session_state:
                st.session_state['logout'] = False

            if 'name' not in st.session_state:
                st.session_state['name'] = None

            if 'username' not in st.session_state:
                st.session_state['username'] = None

            name, auth_status, username = auth.login(location='main')
            if not auth_status:
                st.error("Invalid username/password")
            else:
                user_roles = Auth().get_roles(username)
                if not any(role in user_roles for role in roles):
                    st.error("You are not authorized to view this page")
                    return
                auth.logout(location='sidebar')
                return func(*args, **kwargs)
        return wrapper
    return check
