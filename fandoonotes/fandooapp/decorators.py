from django.http import HttpResponseRedirect, HttpResponse, request
from self import self
import jwt
from django.contrib.auth.models import User
from .service import RedisMethods


# decorators for login
def api_login_required(method):

    def token_verification(ref):
        # getting token from redis cache
        restoken = RedisMethods.get_token(self, 'token')
        # decoding to get user id and username
        decoded_token = jwt.decode(restoken, 'secret', algorithms=['HS256'])
        print("decode token ", decoded_token)
        decoded_id = decoded_token.get('id')
        print("user id", decoded_id)
        user = User.objects.get(id=decoded_id)
        print("username", user)
        # checking the decoded token id into database
        if decoded_id:
            # if token presents in database then only return response
            return method(ref)
        else:
            # else it raises error
            raise PermissionError
    return token_verification
