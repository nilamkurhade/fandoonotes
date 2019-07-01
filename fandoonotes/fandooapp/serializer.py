from rest_framework import serializers
from .models import Notes
from .models import Labels


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
