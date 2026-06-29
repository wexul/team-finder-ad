from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from team_finder.pagination import paginate_queryset

from .forms import LoginForm, ProfileForm, RegistrationForm
from .models import User


def create_user_from_form(form):
    user = form.save(commit=False)
    user.set_password(form.cleaned_data["password"])
    user.save()
    return user


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect("projects:list")

    form = RegistrationForm(request.POST or None)
    if request.method != "POST" or not form.is_valid():
        return render(request, "users/register.html", {"form": form})

    user = create_user_from_form(form)
    login(request, user)
    messages.success(request, "Аккаунт создан")
    return redirect("projects:list")


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("projects:list")

    form = LoginForm(request.POST or None)
    if request.method != "POST" or not form.is_valid():
        return render(request, "users/login.html", {"form": form})

    login(request, form.cleaned_data["user"])
    return redirect("projects:list")


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def participants(request):
    users = User.objects.filter(is_active=True)
    page_obj = paginate_queryset(request, users)
    context = {
        "participants": page_obj.object_list,
        "page_obj": page_obj,
    }
    return render(request, "users/participants.html", context)


def user_detail(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id, is_active=True)
    context = {"profile_user": profile_user, "user_obj": profile_user}
    return render(request, "users/user-details.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def edit_profile(request):
    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )
    if request.method != "POST" or not form.is_valid():
        return render(request, "users/edit_profile.html", {"form": form})

    form.save()
    messages.success(request, "Профиль обновлён")
    return redirect("users:detail", user_id=request.user.pk)


@login_required
@require_http_methods(["GET", "POST"])
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method != "POST" or not form.is_valid():
        return render(request, "users/change_password.html", {"form": form})

    user = form.save()
    update_session_auth_hash(request, user)
    messages.success(request, "Пароль изменён")
    return redirect("users:detail", user_id=request.user.pk)
