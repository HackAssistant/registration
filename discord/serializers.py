from rest_framework import serializers

from discord.models import DiscordUser


class DiscordSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='user.get_type_display', read_only=True)
    name = serializers.CharField(source='user.name', read_only=True)
    team_changed = serializers.BooleanField(write_only=True, required=False)

    @staticmethod
    def add_related_fields(queryset):
        queryset = queryset.select_related('user')
        return queryset

    def update(self, instance, validated_data):
        team_name = validated_data.get('team_name', None)
        team_changed = validated_data.get('team_changed', False)
        if team_changed and team_name is not None and instance.team_name != team_name:
            DiscordUser.objects.filter(team_name=instance.team_name).update(team_name=team_name)
        return super().update(instance, validated_data)

    class Meta:
        model = DiscordUser
        fields = ['discord_id', 'checked_in', 'type', 'name', 'team_name', 'team_changed']
        read_only_fields = ['discord_id']
