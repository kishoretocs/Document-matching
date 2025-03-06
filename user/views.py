from django.shortcuts import render, redirect
from django.contrib.auth.admin import User
from .forms import NewUserCreationForm,UserPasswordChangeForm,CustomAuthenticationForm
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, CreditRequest
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404

def signup(request):
    if request.method == 'POST':
        form  = NewUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request,user)
            return redirect('login')
    else:
        form = NewUserCreationForm()
    return render(request, 'user/signup.html',{'form':form})


def Login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request.POST)  
        if form.is_valid():
            username_or_email = form.cleaned_data.get('username_or_email')
            password = form.cleaned_data.get('password')
            user = form.get_user()
            if user is not None:
                login(request, user)
                return redirect('profile')  
    else:
        form = CustomAuthenticationForm()
    return render(request, 'user/login.html', {'form': form})

def Logout(request):
    logout(request)
    return redirect('login')

@login_required
def change_password(request):
    if request.method=='POST':
        form = UserPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request,user)
            return redirect('profile')
    else:
        form = UserPasswordChangeForm(user=request.user)
    return render(request,'user/change_password.html',{'form':form})

@login_required
def request_credits(request):
    if request.method == "POST":
        try:
            requested_credits = int(request.POST.get("credits"))
            if requested_credits <= 0:
                messages.error(request, "Please request a positive number of credits.")
                return redirect("profile")
        except (TypeError, ValueError):
            messages.error(request, "Invalid number provided.")
            return redirect("profile")

        CreditRequest.objects.create(user=request.user, requested_credits=requested_credits)
        messages.success(request, "Credit request submitted successfully!")
    return redirect("profile")


@staff_member_required
def approve_credits(request, request_id):
    credit_request = get_object_or_404(CreditRequest, id=request_id)
    if not credit_request.approved:
        # Add the requested credits to the user's profile
        profile = credit_request.user.profile
        profile.credits += credit_request.requested_credits
        profile.save()
        credit_request.approved = True
        credit_request.save()
        messages.success(request, f"Approved {credit_request.requested_credits} credits for {credit_request.user.username}.")
    else:
        messages.info(request, "This credit request has already been approved.")
    return redirect("request_list")  # Adjust to your admin dashboard URL


@staff_member_required
def list_credit_requests(request):
    # Get all credit requests that haven't been approved yet, ordered by most recent
    credit_requests = CreditRequest.objects.filter(approved=False).order_by('-created_at')
    approved_requests = CreditRequest.objects.filter(approved=True).order_by('-created_at')
    return render(request, 'user/list.html', {'credit_requests': credit_requests,'approved_request':approved_requests})

@login_required
def scan_document(request):
    profile = request.user.profile
    if profile.credits > 0:
        profile.credits -= 1
        profile.save()
        messages.success(request, "Document scanned successfully! 1 credit deducted.")
        # Here you can integrate your document scan logic
    else:
        messages.error(request, "Not enough credits. Please request additional credits or wait for the daily reset.")
    return redirect("profile")  # Adjust to your dashboard URL
    
@login_required
def profile(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    profile.reset_credits()
    past_request = CreditRequest.objects.filter(user=user).order_by('-created_at')
    return render(request, 'user/profile.html', {
        'credits':profile.credits,
        'username': user.username,
        'email': user.email,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
        'credit_requests': past_request,
    })

