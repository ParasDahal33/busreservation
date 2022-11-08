from email import message
from unicodedata import category
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from btrs_django.settings import MEDIA_ROOT, MEDIA_URL
import json
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from reservationApp.forms import UserRegistration, UpdateProfile, UpdatePasswords, SaveCategory, SaveLocation, SaveBus, SaveSchedule, SaveBooking, PayBooked
from reservationApp.models import Booking, Category, Location, Bus, Schedule
from cryptography.fernet import Fernet
from django.conf import settings
import base64
from datetime import datetime
from django.db.models import Q

context = {
    'page_title': 'File Management System',
}
# login


def login_user(request):
    logout(request)
    resp = {"status": 'failed', 'msg': ''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status'] = 'success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp), content_type='application/json')

# Logout


def logoutuser(request):
    logout(request)
    return redirect('/')

# @login_required


def home(request):
    context['page_title'] = 'Home'
    context['buses'] = Bus.objects.count()
    context['categories'] = Category.objects.count()
    context['upcoming_trip'] = Schedule.objects.filter(
        status=1, schedule__gt=datetime.today()).count()
    return render(request, 'home.html', context)


def registerUser(request):
    user = request.user
    if user.is_authenticated:
        return redirect('home-page')
    context['page_title'] = "Register User"
    if request.method == 'POST':
        data = request.POST
        form = UserRegistration(data)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password1')
            loginUser = authenticate(username=username, password=pwd)
            login(request, loginUser)
            return redirect('home-page')
        else:
            context['reg_form'] = form

    return render(request, 'register.html', context)


@login_required
def update_profile(request):
    context['page_title'] = 'Update Profile'
    user = User.objects.get(id=request.user.id)
    if not request.method == 'POST':
        form = UpdateProfile(instance=user)
        context['form'] = form
        print(form)
    else:
        form = UpdateProfile(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile has been updated")
            return redirect("profile")
        else:
            context['form'] = form

    return render(request, 'manage_profile.html', context)


@login_required
def update_password(request):
    context['page_title'] = "Update Password"
    if request.method == 'POST':
        form = UpdatePasswords(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Your Account Password has been updated successfully")
            update_session_auth_hash(request, form.user)
            return redirect("profile")
        else:
            context['form'] = form
    else:
        form = UpdatePasswords(request.POST)
        context['form'] = form
    return render(request, 'update_password.html', context)


@login_required
def profile(request):
    context['page_title'] = 'Profile'
    return render(request, 'profile.html', context)

# schedule


@login_required
def schedule_mgt(request):
    context['page_title'] = "Trip Schedules"
    schedules = Schedule.objects.all()
    context['schedules'] = schedules

    return render(request, 'schedule_mgt.html', context)


@login_required
def save_schedule(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        if (request.POST['id']).isnumeric():
            schedule = Schedule.objects.get(pk=request.POST['id'])
        else:
            schedule = None
        if schedule is None:
            form = SaveSchedule(request.POST)
        else:
            form = SaveSchedule(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule has been saved successfully.')
            resp['status'] = 'success'
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + "<br>")
    else:
        resp['msg'] = 'No data has been sent.'
    return HttpResponse(json.dumps(resp), content_type='application/json')


@login_required
def manage_schedule(request, pk=None):
    context['page_title'] = "Manage Schedule"
    buses = Bus.objects.filter(status=1).all()
    locations = Location.objects.filter(status=1).all()
    context['buses'] = buses
    context['locations'] = locations
    if not pk is None:
        schedule = Schedule.objects.get(id=pk)
        context['schedule'] = schedule
    else:
        context['schedule'] = {}

    return render(request, 'manage_schedule.html', context)


@login_required
def delete_schedule(request):
    resp = {'status': 'failed', 'msg': ''}

    if request.method == 'POST':
        try:
            schedule = Schedule.objects.get(id=request.POST['id'])
            schedule.delete()
            messages.success(request, 'Schedule has been deleted successfully')
            resp['status'] = 'success'
        except Exception as err:
            resp['msg'] = 'schedule has failed to delete'
            print(err)

    else:
        resp['msg'] = 'Schedule has failed to delete'

    return HttpResponse(json.dumps(resp), content_type="application/json")


# scheduled Trips
@login_required
def scheduled_trips(request):
    if not request.method == 'POST':
        context['page_title'] = "Scheduled Trips"
        schedules = Schedule.objects.filter(
            status=1, schedule__gt=datetime.now()).all()
        context['schedules'] = schedules
        context['is_searched'] = False
        context['data'] = {}
    else:
        context['page_title'] = "Search Result | Scheduled Trips"
        context['is_searched'] = True
        date = datetime.strptime(request.POST['date'], "%Y-%m-%d").date()
        year = date.strftime('%Y')
        month = date.strftime('%m')
        day = date.strftime('%d')
        depart = Location.objects.get(id=request.POST['depart'])
        destination = Location.objects.get(id=request.POST['destination'])
        schedules = Schedule.objects.filter(Q(status=1) & Q(schedule__year=year) & Q(schedule__month=month) & Q(
            schedule__day=day) & Q(Q(depart=depart) | Q(destination=destination))).all()
        context['schedules'] = schedules
        context['data'] = {'date': date,
                           'depart': depart, 'destination': destination}

    return render(request, 'scheduled_trips.html', context)


@login_required
def manage_booking(request, schedPK=None, pk=None):
    context['page_title'] = "Manage Booking"
    context['schedPK'] = schedPK
    if not schedPK is None:
        schedule = Schedule.objects.get(id=schedPK)
        context['schedule'] = schedule
    else:
        context['schedule'] = {}
    if not pk is None:
        book = Booking.objects.get(id=pk)
        context['book'] = book
    else:
        context['book'] = {}

    return render(request, 'manage_book.html', context)


@login_required
def save_booking(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        if (request.POST['id']).isnumeric():
            booking = Booking.objects.get(pk=request.POST['id'])
        else:
            booking = None
        if booking is None:
            form = SaveBooking(request.POST)
        else:
            form = SaveBooking(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            if booking is None:
                booking = Booking.objects.last()
                messages.success(
                    request, f'Booking has been saved successfully. Your Booking Refderence Code is: <b>{booking.code}</b>', extra_tags='stay')
            else:
                messages.success(
                    request, f'<b>{booking.code}</b> Booking has been updated successfully.')
            resp['status'] = 'success'
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + "<br>")
    else:
        resp['msg'] = 'No data has been sent.'

    return HttpResponse(json.dumps(resp), content_type='application/json')


@login_required
def bookings(request):
    context['page_title'] = "Bookings"
    bookings = Booking.objects.all()
    context['bookings'] = bookings

    return render(request, 'bookings.html', context)


@login_required
def view_booking(request, pk=None):
    if pk is None:
        messages.error(request, "Unkown Booking ID")
        return redirect('booking-page')
    else:
        context['page_title'] = 'Vieww Booking'
        context['booking'] = Booking.objects.get(id=pk)
        return render(request, 'view_booked.html', context)


@login_required
def pay_booked(request):
    resp = {'status': 'failed', 'msg': ''}
    if not request.method == 'POST':
        resp['msg'] = "Unknown Booked ID"
    else:
        booking = Booking.objects.get(id=request.POST['id'])
        form = PayBooked(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"<b>{booking.code}</b> has been paid successfully", extra_tags='stay')
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    resp['msg'] += str(error + "<br>")

    return HttpResponse(json.dumps(resp), content_type='application/json')


@login_required
def delete_booking(request):
    resp = {'status': 'failed', 'msg': ''}

    if request.method == 'POST':
        try:
            booking = Booking.objects.get(id=request.POST['id'])
            code = booking.code
            booking.delete()
            messages.success(
                request, f'[<b>{code}</b>] Booking has been deleted successfully')
            resp['status'] = 'success'
        except Exception as err:
            resp['msg'] = 'booking has failed to delete'
            print(err)

    else:
        resp['msg'] = 'booking has failed to delete'

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def find_trip(request):
    context['page_title'] = 'Find Trip Schedule'
    context['locations'] = Location.objects.filter(status=1).all
    today = datetime.today().strftime("%Y-%m-%d")
    context['today'] = today
    return render(request, 'find_trip.html', context)
