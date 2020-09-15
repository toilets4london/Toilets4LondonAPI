from rest_framework import serializers
from Toilets4LondonAPI.toilets4london.models import Toilet


# class ToiletSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     address = serializers.CharField(required=False, allow_blank=True, max_length=500)
#     borough = serializers.CharField(required=False, allow_blank=True, max_length=100)
#
#     def create(self, validated_data):
#         return Toilet.objects.create(**validated_data)
#
#     def update(self, instance, validated_data):
#         """
#         Update and return an existing Toilet instance, given the validated data.
#         """
#         instance.address = validated_data.get('address', instance.address)
#         instance.borough = validated_data.get('borough', instance.borough)
#         instance.save()
#         return instance


class ToiletSerializer(serializers.ModelSerializer):
    """
    shortcut for creating serializer classes:
    An automatically determined set of fields.
    Simple default implementations for the create() and update() methods.
    """
    class Meta:
        model = Toilet
        fields = ['id', 'address','borough']