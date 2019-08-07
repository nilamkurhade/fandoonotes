import json

from .document import NotesDocument
from .serializer import NotesDocumentSerializer
import self as self
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import jwt
from django.utils.decorators import method_decorator
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
from .service import RedisServices
from .models import Notes
from .models import Labels
from .serializer import NoteSerializer
from .serializer import LabelSerializer
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
import pickle
import redis
from .decorators import api_login_required
import logging
from rest_framework.response import Response

from django_elasticsearch_dsl_drf.constants import (
    LOOKUP_FILTER_RANGE,
    LOOKUP_QUERY_IN,
    LOOKUP_QUERY_GT,
    LOOKUP_QUERY_GTE,
    LOOKUP_QUERY_LT,
    LOOKUP_QUERY_LTE,
)
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
    CompoundSearchFilterBackend, FunctionalSuggesterFilterBackend)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet

# This retrieves a Python logging instance (or creates it)
logger = logging.getLogger(__name__)


# view for index
def index(request):
    return render(request, 'fandooapp/Index.html')


@login_required
def special(request):
    return HttpResponse("You are logged in !")


# view for logout
@csrf_exempt
@login_required
def user_logout(request):
    logout(request)
    RedisServices.flush(self)
    return HttpResponseRedirect(reverse('index'))


# view for login and and after login token generation
@csrf_exempt
def user_login(request):
    res =[]
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            if username is None:
                return Response({"error": "username not available"}, status=404)
            if password is None:
                return Response({"error": "password not available"}, status=404)
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    # creating JWT token
                    payload = {
                        'id': user.id,
                        'email': user.email,
                    }
                    jwt_token = jwt.encode(payload, 'secret', 'HS256').decode('utf-8')
                    print("11111111111111", jwt_token)
                    # storing token into redis cache
                    RedisServices.set_token(self, 'token', jwt_token)
                    restoken = RedisServices.get_token(self, 'token')
                    print("token in redis", restoken)
                    login(request, user)
                    message = "you have successfully logged in"
                    res = message
                    result = {
                            'message': res,
                            'username': user.username,
                            'Password': user.password,
                            'Email': user.email,
                            'token': jwt_token,
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
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
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
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
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
# @method_decorator(api_login_required)
def image_upload(request):
    try:
        message = None
        status_code = 500
        if request.method == 'POST':

            # taking input image files
            uploaded_file = request.FILES.get('document')
            print("fsgf",uploaded_file)
            if uploaded_file is None:
                message = "Please select the file to upload"
                status_code = 400
                logger.error(message)
                return JsonResponse({'message': message, 'status': status_code})

            else:
                file_name = 'testing.jpg'
                s3_client = boto3.client('s3')
                s3uploadresponse = s3_client.upload_fileobj(uploaded_file, 'fandoo-static', Key=file_name)
                print('s3', s3uploadresponse)
                message = "Image successfully uploaded"
                status_code = 200     # success msg
                logger.info(message)
                return JsonResponse({'message': message, 'status': status_code})

        else:
            status_code = 400    # bad request
            message = "The request is not valid."
            logger.error(message)
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
    @method_decorator(api_login_required)
    def get(self, request):
        try:
            restoken = RedisServices.get_token(self, 'token')
            decoded_token = jwt.decode(restoken, 'secret', algorithms=['HS256'])
            dec_id = decoded_token.get('id')
            user = User.objects.get(id=dec_id)
            # getting the of particular logged in user
            notes = Notes.objects.filter(created_by=user, trash=False, is_deleted=False, is_archive=False)
            if notes is None:
                message = "Notes not available"
                logger.error(message)
                return Response({"error": message})

            else:
                data = NoteSerializer(notes, many=True).data
                length = len(data)
                print(length, '------------->')
                my_labels = []
                for index in range(0, length):
                    if len(data[index]['labels']) is not 0:
                        for lb in range(0, len(data[index]['labels'])):
                            label_id = data[index]['labels'].pop(lb)
                            print(data[index]['labels'])
                            label_name = Labels.objects.get(id=label_id).label
                            print(label_name)
                            data[index]['labels'].insert(0, label_name)
                # storing notes in redis cache
                r = redis.StrictRedis('localhost')
                mydict = notes
                p_mydict = pickle.dumps(mydict)
                r.set('mydict', p_mydict)
                read_dict = r.get('mydict')
                yourdict = pickle.loads(read_dict)
                print("notes in redis cache", yourdict)
                return Response(data, status=200)
        except Notes.DoesNotExist as e:
            return Response({"error": "Notes not available"}, status=404)

    # to create new note
    @method_decorator(api_login_required)
    def post(self, request):
        restoken = RedisServices.get_token(self, 'token')
        decoded_token = jwt.decode(restoken, 'secret', algorithms=['HS256'])
        print("decode token ", decoded_token)
        dec_id = decoded_token.get('id')
        print("user id", dec_id)
        user = User.objects.get(id=dec_id)
        print("username", user)
        serializer = NoteSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save(created_by=user)
        except serializers.ValidationError:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)


# performing operations on notes like edit, delete
class Notedata(APIView):

    # to get particular object
    def get_object(self, id=None):
        obj = Notes.objects.get(id=id)
        return obj

    # to get id wise note
    def get(self, request, id=None):
        try:
            data = self.get_object(id)
            serializer = NoteSerializer(data).data
            return Response(serializer)
        except Notes.DoesNotExist as e:
            return JsonResponse({"Error": "Note not available of this id"}, status=Response.status_code)

    # editing the particular note
    def put(self, request, id=None, formate=None):

        data = request.data
        instance = self.get_object(id)
        serializer = NoteSerializer(instance, data=data)
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
            return JsonResponse({"Error": "Note Does Not Exist Or Deleted.."}, status=Response.status_code)


# to create the label and list of labels
class LabelList(APIView):

    # list of labels
    @method_decorator(api_login_required)
    def get(self, request, is_deleted=None):
        label = Labels.objects.filter(is_deleted=False)
        serializer = LabelSerializer(label, many=True).data

        print('serializer----<>', serializer)

        length = len(serializer)
        my_labels = []
        for index in range(0, length):
            my_labels.append(serializer[index]['label'])

        print(my_labels)

        return Response(serializer, status=200)

    # creating the new label
    @method_decorator(api_login_required)
    def post(self, request):
        serializer = LabelSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
        except serializers.ValidationError:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse(serializer.data)


# performing operations like edit, delete on labels
class LabelViewDetails(APIView):

    # to get particular object
    def get_object(self, id=None):
        try:
            obj = Labels.objects.get(id=id)
            return obj
        except Notes.DoesNotExist as e:
            return JsonResponse({"error": "Given object not found."}, status=404)

    # to get id wise label

    def get(self, request, id=None):
        try:
            data = self.get_object(id)
            ser = LabelSerializer(data).data
            return Response(ser)
        except Notes.DoesNotExist as e:
            return JsonResponse({"Error": "label not available of this id"}, status=Response.status_code)

    # editing the label
    def put(self, request, id=None):
        try:
            data = request.data
            instance = self.get_object(id)
            if data or instance is None:
                error = "to edit data pass proper data"
                logger.error(error)
            else:
                serializer = LabelSerializer(instance, data=data)
        except Notes.DoesNotExist as e:
            return JsonResponse({"Error": "label not available of this id to edit"}, status=Response.status_code)
        try:
            if serializer.is_valid():
                serializer.save()
        except serializers.ValidationError:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(serializer.data, status=200)

    # deleting the label
    @method_decorator(api_login_required)
    def delete(self, request, id):
        try:
            # GET THE OBJECT OF THAT note_od BY PASSING note_id TO THE get_object() FUNCTION
            instance = self.get_object(id)
            # CHECK THE NOTE is_deleted and is_trashed status Of both are True Then Update Both The Values
            print(instance)
            if instance.is_deleted is False:
                # UPDATE THE is_deleted
                instance.is_deleted = True
                # UPDATE THE is_trashed
                instance.trash = True
                # SAVE THE RECORD
                instance.save()
            # RETURN THE RESPONSE MESSAGE AND CODE
            return Response({"Message": "label Deleted Successfully And Added To The Trash."}, status=200)
            # ELSE EXCEPT THE ERROR AND SEND THE RESPONSE WITH ERROR MESSAGE
        except Notes.DoesNotExist as e:
            return Response({"Error": "label Does Not Exist Or Deleted.."}, status=Response.status_code)


# listing all the notes which are in trash
class NoteTrashView(APIView):
    # listing all the notes which are in trash
    # @method_decorator(api_login_required)
    def get(self, request):
        try:
            restoken = RedisServices.get_token(self, 'token')
            decoded_token = jwt.decode(restoken, 'secret', algorithms=['HS256'])
            print("decode token ", decoded_token)
            dec_id = decoded_token.get('id')
            print("user id", dec_id)
            user = User.objects.get(id=dec_id)
            print("username", user)
            trash_notes = Notes.objects.filter(created_by=user, trash=True)
            data = NoteSerializer(trash_notes, many=True)
            return Response(data.data, status=200)
        except Notes.DoesNotExist as e:
            return JsonResponse({"error": "Notes not available in trash"}, status=404)


# to set the achive note
class NoteTrash(APIView):

    # to get particular object
    def get_object(self, id=None):
        obj = Notes.objects.get(id=id)
        return obj

    def put(self, request, id=None):
        """ This handles PUT request to archive particular note by note id """

        result = {
            "message": "Something bad happened",
            "success": False,
            "data": []
        }
        logger.info("Enter In The PUT Method Set trash API")
        data = request.data['trash']
        print("Data", data)
        try:
            if not id:
                raise ValueError
            logger.debug("Enter In The Try Block")
            # get the note object by passing the note id
            instance = self.get_object(id)
            if not instance:
                raise Notes.DoesNotExist
            # check note is not trash and not deleted

            if not instance.is_archive:
                # update the record and set the archive
                instance.trash = data
                instance.save()
                # return the success message and archive data
                result["message"] = "Archive Set Successfully"
                result["success"] = True
                result["data"] = data
                logger.debug("Return The Response To The Browser..")
                return Response(result, status=200)
        # except the exception and return the response
        except ValueError as e:
            result["Message"] = "Note id cant blank"
            logger.debug("Return The Response To The Browser..")
            return Response(result, status=204)
        except Notes.DoesNotExist as e:
            result["message"] = "No record found for note id "
            logger.debug("Return The Response To The Browser..")
        return Response(result, status=204)


# listing all the notes which are archive
class NoteArchiveview(APIView):
    # @method_decorator(api_login_required)
    def get(self, request):
        try:
            restoken = RedisServices.get_token(self, 'token')
            decoded_token = jwt.decode(restoken, 'secret', algorithms=['HS256'])
            print("decode token ", decoded_token)
            dec_id = decoded_token.get('id')
            print("user id", dec_id)
            user = User.objects.get(id=dec_id)
            print("username", user)
            archive_notes = Notes.objects.filter(created_by=user, is_archive=True)
            print("===========", archive_notes)
            data = NoteSerializer(archive_notes, many=True)
            return Response(data.data, status=200)
        except Notes.DoesNotExist as e:
            error = "Notes not available in Archive"
            logger.exception(error)
            return JsonResponse({"error": "Notes not available in Archive"}, status=404)


# to set the achive note
class NoteArchive(APIView):

    # to get particular object
    def get_object(self, id=None):
        obj = Notes.objects.get(id=id)
        return obj

    def put(self, request, id=None):
        """ This handles PUT request to achieve particular note by note id """

        result = {
            "message": "Something bad happened",
            "success": False,
            "data": []
        }
        logger.info("Enter In The PUT Method Set archive API")
        data = request.data['is_archive']
        print("Data", data)
        try:
            if not id:
                raise ValueError
            logger.debug("Enter In The Try Block")
            # get the note object by passing the note id
            instance = self.get_object(id)
            print(instance, "=====================")
            if not instance:
                raise Notes.DoesNotExist
            # check note is not trash and not deleted

            if not instance.is_archive:
                # update the record and set the archive
                instance.is_archive = data
                instance.save()
                # return the success message and archive data
                result["message"] = "Archive Set Successfully"
                result["success"] = True
                result["data"] = data
                logger.debug("Return The Response To The Browser..")
                return Response(result, status=200)
        # except the exception and return the response
        except ValueError as e:
            result["Message"] = "Note id cant blank"
            logger.debug("Return The Response To The Browser..")
            return Response(result, status=204)
        except Notes.DoesNotExist as e:
            result["message"] = "No record found for note id "
            logger.debug("Return The Response To The Browser..")
        return Response(result, status=204)


# view to search notes data
class NotesDocumentViewSet(DocumentViewSet):
    document = NotesDocument
    serializer_class = NotesDocumentSerializer
    lookup_field = 'id'
    filter_backends = [
        FilteringFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        CompoundSearchFilterBackend,
        FunctionalSuggesterFilterBackend
    ]

    # search in all fields in one request
    search_fields = (
        'title',
        'discription',
        'color',
    )

    # List of filter fields
    filter_fields = {
        'id': {
            'field': 'id',
            'lookups': [
                # to set the extent search,
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
                # to search elements greater than the given value
                LOOKUP_QUERY_GT,
                # to search for the elements equal and greater than the given value
                LOOKUP_QUERY_GTE,
                # to search for the elements lesser than the given value
                LOOKUP_QUERY_LT,
                # to search for the elements equal and lesser than the given value.
                LOOKUP_QUERY_LTE,
            ],
        },
        'title': 'title.raw',
        'discription': 'discription.raw',
        'color': 'color.raw',
    }

    # set ordering fields
    ordering_fields = {
        'title': 'title.raw',
        'discription': 'discription.raw',
        'color': 'color.raw',

    }

    functional_suggester_fields = {
        'title': 'title.raw',
        'discription': 'discription.raw',
    }


class NoteCollaborator(APIView):
    def get_object(self, id=None):
        obj = Notes.objects.get(id=id)
        return obj

    def put(self, request, id=None):
        """ This handles PUT request to collaborate particular note by note id """
        result = {
            "message": "Something bad happened",
            "success": False,
            "data": []
        }
        logger.info("Enter In The PUT Method collaborate API")
        collobrate_data = request.data
        print("collobrate_data",collobrate_data)
        # getting user's email id from input data
        collaborator_email = collobrate_data['collaborate']
        # gettting collaborate user from collaborator email
        collaborate_user = User.objects.filter(email=collaborator_email) & User.objects.filter(is_active=1)
        print("collaborate user", collaborate_user)
        user_id = []
        for i in collaborate_user:
            user_id.append(i.id)
        # getting user id of collaborate_user
        collaborate_id = user_id[0]
        noteinstance = self.get_object(id=id)
        try:
            if not id:
                raise ValueError
            logger.debug("Enter In The Try Block")
            # token of logged in user from redis cache
            restoken = RedisServices.get_token(self, 'token')
            # decoding token to get user id and email of logged in user
            decoded_token = jwt.decode(restoken, 'secret', algorithms=['HS256'])
            decoded_id = decoded_token.get('id')
            decoded_email = decoded_token.get('email')
            user = User.objects.get(id=decoded_id)
            # checking in database that input collaborate email is present in database or not
            if collaborator_email:
                print("data available in database", collaborator_email)
                # checking collaborate email and logged in user email id is same or not
                if collaborator_email is decoded_email:
                    result["message"] = "with same email id can not be collaborate, Please pass the correct email id"
                    result["success"] = False
                    return Response(result, status=400)
                else:
                    # collaborating collaborate user id with note
                    noteinstance.collaborate.add(int(collaborate_id))
                    noteinstance.save()
                    current_site = get_current_site(request)
                    # creating mail body
                    mail_subject = 'collaborated note'
                    message = render_to_string('fandooapp/collaborate_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                    })
                    to_email = collaborator_email
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    print("llllllllll", email)
                    email.send()
                    result["message"] = "Note Collaborated Successfully"
                    result["success"] = True
                    result["data"] = collobrate_data
                    logger.debug("Return The Response To The Browser..")
                    return Response(result, status=200)
            else:
                result["message"] = "Given collaborated email not found in database"
                result["success"] = False
                return Response(result, status=404)
        except ValueError as e:
            result["Message"] = "Note id cant blank"
            logger.debug("Return The Response To The Browser..")
        except Notes.DoesNotExist as e:
            result["message"] = "No record found for note id "
            logger.debug("Return The Response To The Browser..")
        return Response(result, status=200)


class getAllUser(APIView):
    @method_decorator(api_login_required)
    def get(self, request, id=None):
        user = User.objects.all()
        print(user)
        users = []
        if user:
            for email in user:
                users.append(email.email)
                user_list = users
        else:
            return Response('Error ')
        return Response(user_list)
