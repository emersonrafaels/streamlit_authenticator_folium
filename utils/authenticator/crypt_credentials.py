import streamlit_authenticator as stauth

hashed_passwords = stauth.Hasher(['Ourlastnight12@', 'def']).generate()

print(hashed_passwords)