from django.urls import path

from .views import google_logout, authenticate_user_login, register_user, google_login,fetch_users, update_user_role, update_user, delete_user
urlpatterns = [
    path('register', register_user, name='register-user'),
    path('google/signin', google_login, name='google-login'),
    path('logout', google_logout, name='google-logout'),
    path('login', authenticate_user_login, name="user-login"),
    path('updateUserRole', update_user_role, name="update_user_role"),
    path('fetchUsers', fetch_users, name="fetch_users"),
    path('updateUser', update_user, name="update-user"),
    path('deleteUser', delete_user, name="delete_user"),
]