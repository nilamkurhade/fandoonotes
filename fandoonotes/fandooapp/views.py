import json
import self as self
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import jwt
from requests import Response
from rest_framework import serializers, status

from .forms import SignupForm
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .token import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.core.mail import send_mail
import boto3
from django.conf import settings
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from .service import RedisMethods
from django.views.decorators.cache import cache_page
from .models import Notes
from .models import Labels
from .serializer import NoteSerializer
from .serializer import LabelSerializer
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response


# view for index
def index(request):
    return render(request, 'fandooapp/Index.html')


@login_required
def special(request):
    return HttpResponse("You are logged in !")


# view for logout
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


# view for login and and after login token generation
@csrf_exempt
@cache_page(60 * 15)
def user_login(request):
    res =[]
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            # if username is None:
            #     raise
            # if password is None:
            #     raise
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    # creating JWT token
                    payload = {
                        'id': user.id,
                        'email': user.email,
                    }
                    jwt_token = {'token': jwt.encode(payload, "SECRET_KEY")}
                    j_token = jwt_token['token']
                    print("11111111111111", jwt_token)
                    RedisMethods.set_token(self, 'token', j_token)
                    restoken = RedisMethods.get_token(self, 'token')
                    print("token in redis", restoken)
                    login(request, user)
                    message = "you have successfully logged in"
                    res = message
                    result ={
                            'message': res,
                            'username': user.username,
                            'Password': user.password,
                            'status_code': 200

                    }
                    return JsonResponse({'result': result})
                else:
                    message = "Your account was inactive."
                    status_code = 400
                    return JsonResponse({'message': message, 'status': status_code})
            else:
                print("Someone tried to login and failed.")
                print("They used username: {} and password: {}".format(username, password))
                message = "Invalid login details given"
                status_code = 400

                return JsonResponse({'message': message, 'status': status_code})
        else:
            return render(request, 'fandooapp/login.html', {})
    except RuntimeError:
        print(" ")

# view for signup and email verification by sending activation link on users email
@csrf_exempt
def signup(request):
    try:
        if request.method == 'POST':
            form = SignupForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                # creating mail body
                mail_subject = 'Activate your Fundoo notes account.'
                message = render_to_string('fandooapp/account_activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                    'token': account_activation_token.make_token(user),
                })
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(
                            mail_subject, message, to=[to_email]
                )
                print("llllllllll", email)
                email.send()
                return HttpResponse('Please confirm your email address to complete the registration')
        else:
            form = SignupForm()
        return render(request, 'fandooapp/signup.html', {'form': form})
    except RuntimeError:
        print(" ")


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')


# view to sent email
def email(request):
    subject = 'Thank you for registering to our site'
    message = ' it  means a world to us '
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['receiver@gmail.com',]
    send_mail(subject, message, email_from, recipient_list)
    return redirect('redirect to a new page')


# to upload images in s3 bucket
@csrf_exempt
def s3_upload(request):
    try:
        message = None
        status_code = 500
        if request.method == 'POST':
            # taking input image files
            uploaded_file = request.FILES.get('document')
            if uploaded_file is None:
                message = "Empty file can not be uploaded"
                status_code = 400
                return JsonResponse({'message': message, 'status': status_code})
            else:
                file_name = 'nature.jpg'
                s3_client = boto3.client('s3')
                s3_client.upload_fileobj(uploaded_file, 'fandoo-static', Key=file_name)
                message = "Image successfully uploaded"
                status_code = 200     # success msg
                return JsonResponse({'message': message, 'status': status_code})
        else:
            status_code = 400    # bad request
            message = "The request is not valid."
        return JsonResponse({'message': message, 'status': status_code})
    except RuntimeError:
        print(" ")

# view of home for social login
@login_required
def home(request):
    return render(request, 'fandooapp/home1.html')


# to create and display the list of notes
class NotesList(APIView):

    # to get list of notes
    def get(self, request, trash=None, is_archive=None):
        notes = Notes.objects.filter(trash=False, is_archive=False)
        data = NoteSerializer(notes, many=True).data
        return Response(data, status=200)

    # to create new note
    def post(self, request):
        serializer = NoteSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
        except serializers.ValidationError:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.data)


# performing operations on notes like edit, delete
class Notedata(APIView):

    # to get particular object
    def get_object(self, id=None):
        a = Notes.objects.get(id=id)
        return a

    # to get id wise note
    def get(self,request, id=None):
        data = self.get_object(id)
        ser = NoteSerializer(data).data
        return Response(ser)

    # editing the particular note
    def put(self, request, id=None):
        data = request.data
        instance = self.get_object(id)
        serializer = NoteSerializer(instance,  data=data)
        try:
            if serializer.is_valid():
                serializer.save()
        except serializers.ValidationError:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(serializer.data, status=200)

    # deleting the note
    def delete(self, request, id):
        try:
            # GET THE OBJECT OF THAT note_od BY PASSING note_id TO THE get_object() FUNCTION
            instance = self.get_object(id)
            # CHECK THE NOTE is_deleted and is_trashed status Of both are True Then Update Both The Values
            print(instance)
            if instance.is_deleted == False:
                # UPDATE THE is_deleted
                instance.is_deleted = True
                # UPDATE THE is_trashed
                instance.trash = True
                # SAVE THE RECORD
                instance.save()
            # RETURN THE RESPONSE MESSAGE AND CODE
            return Response({"Message": "Note Deleted Successfully And Added To The Trash."}, status=200)
            # ELSE EXCEPT THE ERROR AND SEND THE RESPONSE WITH ERROR MESSAGE
        except Notes.DoesNotExist as e:
            return Response({"Error": "Note Does Not Exist Or Deleted.."}, status=Response.status_code)


# to create the label and list of labels
class LabelList(APIView):

    # list of labels
    def get(self, request, is_deleted=None):

        labels = Labels.objects.filter(is_deleted=True)
        # print(notes)
        data = LabelSerializer(labels, many=True)
        return Response(data.data)

    # creating the new label
    def post(self, request):
        serializer = LabelSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
        except serializers.ValidationError:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.data)


# performing operations like edit, delete on labels
class LabelViewDetails(APIView):

    # to get particular object
    def get_object(self, id=None):
        try:
            a = Labels.objects.get(id=id)
            return a
        except Notes.DoesNotExist as e:
            return Response({"error": "Given object not found."}, status=404)

    # to get id wise label
    def get(self, request, id=None):
        data = self.get_object(id)
        ser = LabelSerializer(data).data
        return Response(ser)

    # editing the label
    def put(self, request, id=None):
        data = request.data
        instance = self.get_object(id)
        serializer = LabelSerializer(instance,  data=data)
        try:
            if serializer.is_valid():
                serializer.save()
        except serializers.ValidationError:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(serializer.data, status=200)

    # deleting the label
    def delete(self, request, id):
        try:
            # GET THE OBJECT OF THAT note_od BY PASSING note_id TO THE get_object() FUNCTION
            instance = self.get_object(id)
            # CHECK THE NOTE is_deleted and is_trashed status Of both are True Then Update Both The Values
            print(instance)
            if instance.is_deleted == False:
                # UPDATE THE is_deleted
                instance.is_deleted = True
                # UPDATE THE is_trashed
                instance.trash = True
                # SAVE THE RECORD
                instance.save()
            # RETURN THE RESPONSE MESSAGE AND CODE
            return Response({"Message": "Note Deleted Successfully And Added To The Trash."}, status=200)
            # ELSE EXCEPT THE ERROR AND SEND THE RESPONSE WITH ERROR MESSAGE
        except Notes.DoesNotExist as e:
            return Response({"Error": "Note Does Not Exist Or Deleted.."}, status=Response.status_code)


# listing all the notes which are in trash
class NoteTrashView(APIView):

    def get(self, request, trash=None):
        notes = Notes.objects.filter(trash=True)
        data = NoteSerializer(notes, many=True)
        return Response(data.data, status=200)


# listing all the notes which are archive
class NoteArchiveview(APIView):
    def get(self, request, is_archive=None):
        notes = Notes.objects.filter(is_archive=True)
        data = NoteSerializer(notes, many=True)
        return Response(data.data, status=200)
