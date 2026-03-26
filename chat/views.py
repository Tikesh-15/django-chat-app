from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models, transaction
from .models import Message, Profile, Contact, StrangerQueue
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import uuid
# --- 1. STRANGER CHAT LOGIC (Fully Synced) ---

@login_required
def stranger_chat(request):
    return render(request, 'stranger_chat.html')
@login_required
def check_room(request):
    user = request.user
    
    # STEP 1: Pehle check karo kya main already kisi room mein match ho chuka hoon?
    my_entry = StrangerQueue.objects.filter(user=user, is_matched=True).first()
    if my_entry:
        room_id = my_entry.room_id
        print(f">>> DEBUG: User {user.username} matched with Room: {room_id}")
        my_entry.delete()  # Match mil gaya, ab entry ki zaroorat nahi
        return JsonResponse({'room_id': room_id})

    # STEP 2: Ab check karo kya koi doosra banda "Waiting" hai?
    # exclude(user=user) zaroori hai taaki khud se match na ho jao
    with transaction.atomic():
        stranger = StrangerQueue.objects.filter(is_matched=False).exclude(user=user).first()

        if stranger:
            # Match mil gaya! Ek naya room banao
            new_room = f"TheFoodHouse_{uuid.uuid4().hex[:10]}"
            print(f">>> DEBUG: Match Found! {user.username} connecting to {stranger.user.username}")
            
            # Stranger ki entry update karo taaki usse room_id mil jaye
            stranger.room_id = new_room
            stranger.is_matched = True
            stranger.save()
            
            # Jo banda match "dhund raha hai" (yani aap), wo seedha room join karega
            return JsonResponse({'room_id': new_room})
        
        else:
            # STEP 3: Koi nahi mila, toh apni entry banao/update karo (Waiting list mein)
            obj, created = StrangerQueue.objects.update_or_create(
                user=user, 
                defaults={'is_matched': False, 'room_id': None}
            )
            print(f">>> Request from: {user.username} - Device: {request.META.get('HTTP_USER_AGENT')}")
            # print(f">>> DEBUG: User {user.username} is waiting...")
            return JsonResponse({'room_id': None})
@login_required
def clear_waiting(request):
    StrangerQueue.objects.filter(user=request.user).delete()
    return JsonResponse({'status': 'cleared'})

# --- 2. USER AUTH & PROFILE ---
def profile_view(request):
    profile = request.user.profile  # Ya jo bhi tera logic hai
    if request.method == 'POST':
        # Yahan 'request.FILES' hona zaroori hai!
        avatar = request.FILES.get('avatar')
        new_username = request.POST.get('username')
        
        if avatar:
            profile.avatar = avatar
        
        request.user.username = new_username
        request.user.save()
        profile.save()
        return redirect('profile')
    
    return render(request, 'profile.html', {'profile': profile})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            messages.success(request, "Account created! Please login.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        new_username = request.POST.get('username')
        if new_username:
            request.user.username = new_username
            request.user.save()
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
            profile.save()
        messages.success(request, "Profile updated!")
        return redirect('profile_view') 
    return render(request, 'profile.html', {'profile': profile})

# URL name 'profile' ke liye alias (Jo tune manga tha)
@login_required
def profile(request):
    return profile_view(request)


# --- 3. DASHBOARD & MESSAGING ---

@login_required
def index(request):
    users = User.objects.exclude(id=request.user.id)
    user_contacts = Contact.objects.filter(user=request.user)
    nickname_dict = {c.friend_id: c.nickname for c in user_contacts}
    
    for u in users:
        u.nickname = nickname_dict.get(u.id)
        u.unread_count = Message.objects.filter(
            sender=u, receiver=request.user, is_read=False
        ).count()
    
    return render(request, 'index.html', {'users': users})

@login_required
def chat_room(request, username):
    receiver = User.objects.get(username=username)
    Message.objects.filter(sender=receiver, receiver=request.user, is_read=False).update(is_read=True)
    
    contact = Contact.objects.filter(user=request.user, friend=receiver).first()
    if contact:
        receiver.nickname = contact.nickname

    messages_list = Message.objects.filter(
        (models.Q(sender=request.user) & models.Q(receiver=receiver)) |
        (models.Q(sender=receiver) & models.Q(receiver=request.user))
    ).exclude(deleted_by=request.user).order_by('timestamp')

    return render(request, 'chat_room.html', {'receiver': receiver, 'messages': messages_list})

@login_required
def set_nickname(request):
    if request.method == 'POST':
        friend_id = request.POST.get('friend_id')
        new_nickname = request.POST.get('nickname')
        friend_user = User.objects.get(id=friend_id)
        Contact.objects.update_or_create(user=request.user, friend=friend_user, defaults={'nickname': new_nickname})
        return redirect('index')

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('chat_file'):
        myfile = request.FILES['chat_file']
        receiver_id = request.POST.get('receiver_id')
        receiver = User.objects.get(id=receiver_id)
        
        # Message create karo file ke saath
        msg = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=f"📎 Attachment: {myfile.name}",
            file=myfile # Ensure tere Message model mein 'file' field hai
        )
        
        return JsonResponse({
            'status': 'ok',
            'file_url': msg.file.url,
            'file_name': myfile.name
        })
    return JsonResponse({'status': 'error'}, status=400)
@login_required
def clear_chat(request, username):
    receiver = User.objects.get(username=username)
    chat_messages = Message.objects.filter(
        (models.Q(sender=request.user) & models.Q(receiver=receiver)) |
        (models.Q(sender=receiver) & models.Q(receiver=request.user))
    )
    for msg in chat_messages:
        msg.deleted_by.add(request.user)
    messages.success(request, "Chat cleared for you.")
    return redirect('chat_room', username=username)

@login_required
def block_user(request, username):
    target_user = User.objects.get(username=username)
    profile, created = Profile.objects.get_or_create(user=request.user)
    if target_user in profile.blocked_users.all():
        profile.blocked_users.remove(target_user)
        messages.info(request, f"Unblocked {username}")
    else:
        profile.blocked_users.add(target_user)
        messages.warning(request, f"Blocked {username}")
    return redirect('index')

def password_reset_simple(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        new_pass = request.POST.get('new_password')
        try:
            user = User.objects.get(username=uname)
            user.set_password(new_pass)
            user.save()
            messages.success(request, "Password updated successfully!")
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "User not found!")
    return render(request, 'password_reset.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Login logic...
            return redirect('index')
        else:
            # AGAR LOGIN FAIL HUA: Form ko wapas bhejo errors ke saath
            return render(request, 'login.html', {'form': form})
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})