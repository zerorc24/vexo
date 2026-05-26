from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone

from .models import Room, Message, Profile
from .forms import RegisterForm, LoginForm


# ==========================================
# CHAT LIST
# ==========================================
@login_required
def chat_list(request):

    rooms = (
        Room.objects
        .filter(participants=request.user)
        .prefetch_related("participants", "messages")
        .distinct()
    )

    users = User.objects.exclude(id=request.user.id)

    query = request.GET.get("q")

    if query:
        users = users.filter(
            username__icontains=query
        )

    return render(request, "messaging/chat_list.html", {
        "rooms": rooms,
        "users": users,
    })


# ==========================================
# CHAT DETAIL
# ==========================================
@login_required
def chat_detail(request, room_id):

    room = get_object_or_404(
        Room,
        id=room_id
    )

    # SECURITY CHECK
    if request.user not in room.participants.all():
        return redirect("chat_list")

    messages = (
        room.messages
        .select_related("sender")
        .order_by("created_at")
    )

    other_user = (
        room.participants
        .exclude(id=request.user.id)
        .first()
    )

    # MARK AS READ
    Message.objects.filter(
        room=room,
        is_read=False
    ).exclude(
        sender=request.user
    ).update(
        is_read=True
    )

    return render(request, "messaging/chat_detail.html", {
        "room": room,
        "messages": messages,
        "other_user": other_user,
    })


# ==========================================
# SEND MESSAGE (AJAX / FETCH)
# ==========================================
@login_required
def send_message(request, room_id):

    if request.method != "POST":
        return redirect("chat_list")

    room = get_object_or_404(
        Room,
        id=room_id
    )

    if request.user not in room.participants.all():
        return redirect("chat_list")

    content = request.POST.get("content")

    image = request.FILES.get("image")
    voice = request.FILES.get("voice")

    if content or image or voice:

        Message.objects.create(
            room=room,
            sender=request.user,
            content=content if content else "",
            image=image,
            voice=voice
        )

        room.updated_at = timezone.now()
        room.save()

    return redirect("chat_detail", room_id=room.id)


# ==========================================
# START CHAT
# ==========================================
@login_required
def start_chat(request, user_id):

    other_user = get_object_or_404(
        User,
        id=user_id
    )

    # PREVENT SELF CHAT
    if other_user == request.user:
        return redirect("chat_list")

    ids = sorted([
        request.user.id,
        other_user.id
    ])

    room_name = f"dm_{ids[0]}_{ids[1]}"

    room, created = Room.objects.get_or_create(
        name=room_name,
        defaults={
            "room_type": "private"
        }
    )

    room.participants.set([
        request.user,
        other_user
    ])

    return redirect(
        "chat_detail",
        room_id=room.id
    )


# ==========================================
# USERS LIST
# ==========================================
@login_required
def users_list(request):

    users = (
        User.objects
        .exclude(id=request.user.id)
        .select_related("profile")
    )

    query = request.GET.get("q")

    if query:
        users = users.filter(
            username__icontains=query
        )

    return render(request, "messaging/users_list.html", {
        "users": users
    })


# ==========================================
# PROFILE
# ==========================================
@login_required
def profile_view(request):

    profile, created = (
        Profile.objects.get_or_create(
            user=request.user
        )
    )

    return render(request, "messaging/profile.html", {
        "profile": profile
    })


# ==========================================
# LOGIN
# ==========================================
def login_view(request):

    form = LoginForm(
        request.POST or None
    )

    if request.method == "POST":

        if form.is_valid():

            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"]
            )

            if user:

                login(request, user)

                profile, created = (
                    Profile.objects.get_or_create(
                        user=user
                    )
                )

                profile.online = True
                profile.last_seen = timezone.now()
                profile.save()

                return redirect("chat_list")

    return render(request, "messaging/login.html", {
        "form": form
    })


# ==========================================
# REGISTER
# ==========================================
def register_view(request):

    form = RegisterForm(
        request.POST or None
    )

    if request.method == "POST":

        if form.is_valid():

            user = form.save()

            Profile.objects.get_or_create(
                user=user
            )

            login(request, user)

            return redirect("chat_list")

    return render(request, "messaging/register.html", {
        "form": form
    })


# ==========================================
# LOGOUT
# ==========================================
@login_required
def logout_view(request):

    profile = (
        Profile.objects
        .filter(user=request.user)
        .first()
    )

    if profile:

        profile.online = False

        profile.last_seen = timezone.now()

        profile.save()

    logout(request)

    return redirect("login")