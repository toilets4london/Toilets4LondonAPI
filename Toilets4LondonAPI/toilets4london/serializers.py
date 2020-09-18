from rest_framework import serializers
from Toilets4LondonAPI.toilets4london.models import Toilet, Rating
from django.contrib.auth.models import User
from collections import Counter
from rest_framework.reverse import reverse


class ToiletSerializer(serializers.HyperlinkedModelSerializer):
    """
    shortcut for creating serializer classes:
    An automatically determined set of fields.
    Simple default implementations for the create() and update() methods.
    """

    # The untyped ReadOnlyField is always read-only,
    # and will be used for serialized representations,
    # but will not be used for updating model instances
    # when they are deserialized.
    # We could have also used CharField(read_only=True) here.

    owner = serializers.ReadOnlyField(source='owner.username')
    ratings = serializers.SerializerMethodField('get_ratings_detail')

    class Meta:
        model = Toilet
        fields = ['url',
                  'id',
                  'owner',
                  'address',
                  'borough',
                  'latitude',
                  'longitude',
                  'opening_hours',
                  'wheelchair',
                  'name',
                  'ratings',]


    def get_ratings_detail(self, obj):
        ratings = Rating.objects.filter(toilet=obj)
        ratings = Counter(ratings.values_list("rating", flat=True))
        return {f"rating{star}_star": count for star, count in ratings.items()}


class UserSerializer(serializers.HyperlinkedModelSerializer):
    toilets = serializers.HyperlinkedRelatedField(many=True, view_name='toilet-detail',read_only=True)

    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'toilets']


class RatingSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    toilet = serializers.PrimaryKeyRelatedField(queryset=Toilet.objects.all())
    toilet_url = serializers.SerializerMethodField('get_toilet_url', read_only=True)

    class Meta:
        model = Rating
        fields = ['url', 'toilet', 'toilet_url', 'user', 'rating']

    def get_toilet_url(self, obj):
        request = self.context['request']
        return reverse('toilet-detail', args=[obj.toilet.pk], request=request)

