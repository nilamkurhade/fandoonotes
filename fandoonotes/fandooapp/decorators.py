from django.http import HttpResponseRedirect, HttpResponse, request
from self import self
import jwt
from django.contrib.auth.models import User
from .service import RedisMethods


# decorators for login
def api_login_required(method):

    def token_verification(ref):

        restoken = RedisMethods.get_token(self, 'token')
        decoded_token = jwt.decode(restoken, 'secret', algorithms=['HS256'])
        print("decode token ", decoded_token)
        dec_id = decoded_token.get('id')
        print("user id", dec_id)
        user = User.objects.get(id=dec_id)
        print("username", user)
        if dec_id:
            return method(ref)
        else:
            raise PermissionError

    return token_verification
