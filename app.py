
# app.py
import streamlit as st
from auth import get_redis_client, register_user, verify_login

st.set_page_config(page_title="Redis + Streamlit Auth", page_icon="🔐", layout="centered")

# Initialize Redis client once
if "redis" not in st.session_state:
    st.session_state.redis = get_redis_client()

# Session user holder
if "user" not in st.session_state:
    st.session_state.user = None

def show_header():
    left, right = st.columns([1,1])
    with left:
        st.title("🔐 Simple Auth")
        st.caption("Powered by Redis + Streamlit")
    with right:
        if st.session_state.user:
            st.success(f"Signed in as: {st.session_state.user.get('name')} ({st.session_state.user.get('email')})")
            if st.button("Logout"):
                st.session_state.user = None
                st.toast("Logged out")

def show_register():
    st.subheader("Create an account")
    with st.form("register_form", clear_on_submit=False):
        name = st.text_input("Full name", placeholder="Jane Doe")
        email = st.text_input("Email", placeholder="jane@example.com")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")
        agree = st.checkbox("I agree to the Terms of Service")

        submitted = st.form_submit_button("Register")
        if submitted:
            if not agree:
                st.warning("Please agree to the Terms of Service.")
            elif not name or not email or not password:
                st.error("All fields are required.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                ok = register_user(st.session_state.redis, name, email, password)
                if ok:
                    st.success("Account created! You can now log in.")
                    st.balloons()
                else:
                    st.error("Email already registered. Try logging in.")

def show_login():
    st.subheader("Log in")
    with st.form("login_form", clear_on_submit=True):
        email = st.text_input("Email", placeholder="jane@example.com")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")
        if submitted:
            user = verify_login(st.session_state.redis, email, password)
            if user:
                st.session_state.user = user
                st.toast("Logged in successfully")
            else:
                st.error("Invalid email or password.")

def show_app():
    st.header("Welcome 👋")
    st.write(
        "This is a protected area. You only see this when logged in."
    )
    st.info("Replace with your actual app contents.")

def main():
    show_header()
    tabs = st.tabs(["Register", "Login", "App"])
    with tabs[0]:
        show_register()
    with tabs[1]:
        show_login()
    with tabs[2]:
        if st.session_state.user:
            show_app()
        else:
            st.warning("Please log in to access the app.")

if __name__ == "__main__":
    main()
