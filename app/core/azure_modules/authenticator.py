from datetime import datetime, timedelta

import bcrypt
import streamlit as st
from streamlit_authenticator import Authenticate

from app.core.models.logger import db_logger
from models.users import User


class WebAuthenticate(Authenticate):

    @db_logger
    def _check_credentials(self, inplace: bool = True) -> bool:
        """
        Checks the validity of the entered credentials.

        Parameters
        ----------
        inplace: bool
            Inplace setting, True: authentication status will be stored in session state,
            False: authentication status will be returned as bool.
        Returns
        -------
        bool
            Validity of entered credentials.
        """
        user = User.find_user_by_email(self.username)
        if not user or not bcrypt.checkpw(self.password.encode(), user.pwd.encode()) or len(user.authorizations) == 0:
            st.session_state['authentication_status'] = False
            return False

        st.session_state['name'] = user.f_name
        st.session_state['authorizations'] = user.authorizations
        self.exp_date = self._set_exp_date()
        self.token = self._token_encode()
        self.cookie_manager.set(self.cookie_name, self.token,
                                expires_at=datetime.now() + timedelta(days=self.cookie_expiry_days))
        st.session_state['authentication_status'] = True

    @db_logger
    def _check_cookie(self):
        """
        Checks the validity of the reauthentication cookie.
        """
        self.token = self.cookie_manager.get(self.cookie_name)
        if self.token is not None:
            self.token = self._token_decode()
            if self.token is not False:
                if not st.session_state['logout']:
                    if self.token['exp_date'] > datetime.utcnow().timestamp():
                        if 'name' and 'username' in self.token:
                            st.session_state['name'] = self.token['name']
                            st.session_state['username'] = self.token['username']
                            st.session_state['authentication_status'] = True
                            user = User.find_user_by_email(self.token['username'])
                            st.session_state['authorizations'] = []
                            if user:
                                st.session_state['authorizations'] = user.authorizations
