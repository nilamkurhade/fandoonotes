from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework import serializers
from .models import Notes
from .models import Labels
from .document import NotesDocument


# serializer class for notes
class NoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notes
        fields = '__all__'


# serializer class for labels
class LabelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Labels
        fields = '__all__'


class NotesDocumentSerializer(DocumentSerializer):
    title = serializers.CharField(read_only=True)
    discription = serializers.CharField(read_only=True)
    color = serializers.CharField(read_only=True)

    class Meta:
        document = NotesDocument
        fields = ('id', 'title', 'discription', 'color')
