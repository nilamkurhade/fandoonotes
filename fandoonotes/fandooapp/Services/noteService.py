from rest_framework import request
# from serializer import NoteSerializer
from fandooapp.serializer import NoteSerializer


class NoteServices:
    def __init__(self):
        pass

    def create_note(self):
        serializer = NoteSerializer(data=request.data)
        pass