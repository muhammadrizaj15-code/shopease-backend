from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View

from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm
from orders.models import Order


# =========================================================
# REGISTER
# =========================================================
class RegisterView(View):
    template_name = 'accounts/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('products:home')
        form = RegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account was created successfully.")
            return redirect('products:home')
        messages.error(request, "Please correct the errors below.")
        return render(request, self.template_name, {'form': form})


# =========================================================
# LOGIN
# =========================================================
class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('products:home')
        form = AuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                next_url = request.GET.get('next')
                return redirect(next_url or 'products:home')
        messages.error(request, "Invalid username or password.")
        return render(request, self.template_name, {'form': form})


# =========================================================
# LOGOUT
# =========================================================
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('products:home')


# =========================================================
# PROFILE (view + edit)
# =========================================================
@login_required
def profile_view(request):
    """Display and update the logged-in user's profile & address."""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('accounts:profile')
        messages.error(request, "Please correct the errors below.")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {'u_form': u_form, 'p_form': p_form}
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # keep the user logged in
            messages.success(request, "Your password was changed successfully.")
            return redirect('accounts:profile')
        messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def order_history(request):
    """List all past orders for the logged-in user."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/order_history.html', {'orders': orders})
