from rest_framework import serializers
from Toilets4LondonAPI.toilets4london.models import Toilet, Rating, Toilets4LondonUser, Report
from collections import Counter
from rest_framework.reverse import reverse


class ToiletSerializer(serializers.HyperlinkedModelSerializer):
    ratings = serializers.SerializerMethodField('get_ratings_detail')
    reports = serializers.SerializerMethodField('get_reports_detail')

    class Meta:
        model = Toilet
        fields = ['url',
                  'id',
                  'address',
                  'borough',
                  'latitude',
                  'longitude',
                  'opening_hours',
                  'wheelchair',
                  'baby_change',
                  'name',
                  'ratings',
                  'reports']

    def get_ratings_detail(self, obj):
        ratings = Rating.objects.filter(toilet=obj)
        ratings = Counter(ratings.values_list("rating", flat=True))
        return {f"rating{star}_star": count for star, count in ratings.items()}

    def get_reports_detail(self, obj):
        reports = Report.objects.filter(toilet=obj)
        reports = Counter(reports.values_list("reason", flat=True))
        return {f"Reported_{problem}": count for problem, count in reports.items()}


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
        fields = ['id','toilet', 'toilet_url', 'user', 'rating', 'date']

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
