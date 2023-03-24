from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages

from django.urls import reverse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .models import Business, Listing, Neighborhood


def index_view(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    return render(
        request,
        "users/index.html",
        {
            "welcome": "Welcome {}!".format(request.user.first_name),
            "message": "Welcome, {}".format(request.user.first_name),
        },
    )


def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request, "users/login.html", {"message": "Invalid credentials."}
            )

    return render(request, "users/login.html", {"message": "Please log in."})


def register_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 != password2:
            return render(
                request, "users/register.html", {"message": "Passwords must match."}
            )

        if User.objects.filter(email=email).exists():
            return render(
                request, "users/register.html", {"message": "Email already exists."}
            )

        user = User.objects.create_user(
            email=email,
            password=password1,
            first_name=request.POST["first_name"],
            last_name=request.POST["last_name"],
            username=email,
        )
        user = authenticate(request, username=email, password=password1)

        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    return render(request, "users/register.html", {"message": "Please register."})


def logout_view(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    logout(request)

    return render(request, "users/logout.html", {"message": "LOGGED OUT!"})


def add_business_view(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    if request.method == "POST":
        business = Business(
            name=request.POST["name"],
            address=request.POST["address"],
            email=request.POST["email"],
            phone=request.POST["phone"],
            owner=request.user,
        )
        business.save()

        return HttpResponseRedirect(reverse("view_my_businesses"))

    return render(request, "users/add_business.html", {"message": "Add your business."})


def view_business_view(request, business_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    business = Business.objects.get(id=business_id)

    return render(
        request,
        "users/view_business.html",
        {
            "message": "View your business.",
            "business": business,
        },
    )


def update_user(request):
    if not request.user.is_authenticated:
        messages.error(request, "You are not authorized to view this page!")
        return HttpResponseRedirect(reverse("login"))
    else:
        if request.method == "POST":
            user = User.objects.get(pk=request.user.pk)
            email = request.POST["email"]
            # Check if the new email is used by any other users or not
            if user.email != email and User.objects.filter(email=email).exists():
                return render(
                    request,
                    "users/update_user.html",
                    {"message": "Email already exists."},
                )

            user.username = request.POST["email"]
            user.email = request.POST["email"]
            user.first_name = request.POST["first_name"]
            user.last_name = request.POST["last_name"]
            user.save()
            messages.success(request, "Profile Updated Successfuly.")
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "users/update_user.html",
                {"user": User.objects.get(pk=request.user.pk)},
            )


def update_password(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    else:
        if request.method == "POST":
            current_password = request.POST["current_password"]
            username = request.user.username
            password1 = request.POST["password1"]
            password2 = request.POST["password2"]
            if password1 != password2:
                return render(
                    request,
                    "users/update_password.html",
                    {"message": "Passwords must match."},
                )

            u = User.objects.get(pk=request.user.pk)
            if u.check_password(current_password):
                u.set_password(password1)
                u.save()
                login(request, u)
            else:
                return render(
                    request, "users/update_password.html", {"message": "Wrong password"}
                )

            return render(
                request,
                "users/update_user.html",
                {"message": "Password Updated Successfuly"},
            )

        else:
            return render(request, "users/update_password.html")


def delete_user(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    if request.method == "POST":
        password = request.POST["password"]
        u = User.objects.get(pk=request.user.pk)
        if u.check_password(password):
            u.delete()
            return render(request, "users/logout.html", {"message": "Account Deleted"})
        else:
            return render(
                request, "users/delete_user.html", {"message": "Wrong password"}
            )

    else:
        return render(request, "users/delete_user.html")


def view_all_businesses_view(request):
    businesses = Business.objects.all()

    return render(
        request,
        "users/view_all_businesses.html",
        {
            "businesses": businesses,
        },
    )


def view_my_businesses(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    businesses = Business.objects.filter(owner=request.user)

    return render(
        request,
        "users/view_my_businesses.html",
        {
            "businesses": businesses,
        },
    )


def add_listing(request):
    if not request.user.is_authenticated:
        messages.error(request, "You are not authorized to view this page!")
        return HttpResponseRedirect(reverse("login"))
    else:
        if request.method == "POST":
            n = Neighborhood.objects.get(pk=request.POST["neighborhood"])
            listing = Listing(
                title=request.POST["title"],
                description=request.POST["description"],
                price=request.POST["price"],
                email=request.POST["email"],
                phone=request.POST["phone"],
                address=request.POST["address"],
                owner=request.user,
                neighborhood=n,
            )
            listing.save()
            messages.success(request, "Listing was added successfuly!")
            return HttpResponseRedirect(reverse("view_listing", args=(listing.id,)))
        else:
            neighborhoods = Neighborhood.objects.all()
            return render(
                request,
                "users/add_listing.html",
                {"message": "Add your listing.", "neighborhoods": neighborhoods},
            )


def view_listing(request, listing_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    listing = Listing.objects.get(id=listing_id)

    return render(
        request,
        "users/view_listing.html",
        {
            "message": "",
            "listing": listing,
        },
    )


def marketplace(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    listings = Listing.objects.all()

    return render(
        request,
        "users/marketplace.html",
        {
            "listings": listings,
        },
    )
