from django.urls import path
from . import views

urlpatterns = [

    # CHAT LIST
    path(
        "",
        views.chat_list,
        name="chat_list"
    ),

    # CHAT DETAIL (FIXED: use ID, not room name)
    path(
        "chat/<int:room_id>/",
        views.chat_detail,
        name="chat_detail"
    ),

    # START CHAT
    path(
        "start/<int:user_id>/",
        views.start_chat,
        name="start_chat"
    ),

    # USERS LIST
    path(
        "users/",
        views.users_list,
        name="users_list"
    ),

    # PROFILE
    path(
        "profile/",
        views.profile_view,
        name="profile"
    ),

    # AUTH
    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "register/",
        views.register_view,
        name="register"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),
]