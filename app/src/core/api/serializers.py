from rest_framework import serializers

from src.core import models


class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Node
        fields = ('id', 'public_key', 'height', 'network_weight', 'total_stake', 'active_bid', 'percent_of_network',)


class ScoringSerializer(serializers.ModelSerializer):
    node = NodeSerializer()

    class Meta:
        model = models.Scoring
        fields = '__all__'


class ScoreSerializer(serializers.ModelSerializer):
    node = NodeSerializer()

    class Meta:
        model = models.Score
        fields = '__all__'
