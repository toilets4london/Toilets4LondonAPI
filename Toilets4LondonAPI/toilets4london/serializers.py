from rest_framework import serializers
from Toilets4LondonAPI.toilets4london.models import Toilet, Rating, Toilets4LondonUser, Report
from rest_framework.reverse import reverse
from django.db.models import Avg


class ToiletSerializer(serializers.HyperlinkedModelSerializer):

    def average_rating(self, obj):
        result = Rating.objects.filter(toilet=obj).aggregate(Avg("rating"))
        avg = result["rating__avg"]
        if avg:
            return round(avg)
        return None

    rating = serializers.SerializerMethodField('average_rating')

    class Meta:
        model = Toilet
        fields = ['url',
                  'id',
                  'data_source',
                  'name',
                  'address',
                  'borough',
                  'latitude',
                  'longitude',
                  'opening_hours',
                  'wheelchair',
                  'baby_change',
                  'fee',
                  'covid',
                  'rating']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Toilets4LondonUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']


class RatingSerializer(serializers.ModelSerializer):

    user = serializers.ReadOnlyField(source='user.pk')
    toilet = serializers.PrimaryKeyRelatedField(queryset=Toilet.objects.all())
    toilet_url = serializers.SerializerMethodField('get_toilet_url', read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'toilet', 'toilet_url', 'user', 'rating', 'date']

    def get_toilet_url(self, obj):
        request = self.context['request']
        return reverse('toilet-detail', args=[obj.toilet.pk], request=request)


class ReportSerializer(serializers.ModelSerializer):

    user = serializers.ReadOnlyField(source='user.pk')
    toilet = serializers.PrimaryKeyRelatedField(queryset=Toilet.objects.all())
    toilet_url = serializers.SerializerMethodField('get_toilet_url', read_only=True)

    class Meta:
        model = Report
        fields = ['id','toilet', 'toilet_url', 'user', 'reason', 'other_description', 'date']

    def get_toilet_url(self, obj):
        request = self.context['request']
        return reverse('toilet-detail', args=[obj.toilet.pk], request=request)


class CustomTokenSerializer(serializers.Serializer):
    token = serializers.CharField()
