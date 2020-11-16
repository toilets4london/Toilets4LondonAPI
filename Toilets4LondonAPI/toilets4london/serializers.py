from rest_framework import serializers
from Toilets4LondonAPI.toilets4london.models import Toilet, Rating, Toilets4LondonUser, Report
from rest_framework.reverse import reverse


class ToiletSerializer(serializers.HyperlinkedModelSerializer):

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Toilet
        exclude = ['num_ratings']
        read_only_fields = ['rating']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Toilets4LondonUser
        fields = '__all__'


class RatingSerializer(serializers.ModelSerializer):

    def get_toilet_url(self, obj):
        request = self.context['request']
        return reverse('toilet-detail', args=[obj.toilet.pk], request=request)

    toilet_url = serializers.SerializerMethodField('get_toilet_url')

    class Meta:
        model = Rating
        exclude = ()


class ReportSerializer(serializers.ModelSerializer):

    def get_toilet_url(self, obj):
        request = self.context['request']
        return reverse('toilet-detail', args=[obj.toilet.pk], request=request)

    toilet_url = serializers.SerializerMethodField('get_toilet_url')

    class Meta:
        model = Report
        exclude = ()


class CustomTokenSerializer(serializers.Serializer):
    token = serializers.CharField()
