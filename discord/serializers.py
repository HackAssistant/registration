from rest_framework import serializers

from discord.models import DiscordUser


class DiscordSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='user.get_type_display', read_only=True)
    name = serializers.CharField(source='user.name', read_only=True)
    team_changed = serializers.BooleanField(write_only=True, required=False)
    team_created = serializers.BooleanField(write_only=True, required=False)
    checked_in = serializers.BooleanField(required=False)
    stickers = serializers.CharField(required=False)

    @staticmethod
    def add_related_fields(queryset):
        queryset = queryset.select_related('user')
        return queryset

    def change_team_name(self, instance, validated_data):
        team_name = validated_data.get('team_name', None)
        team_changed = validated_data.get('team_changed', False)
        if team_changed and team_name is not None and instance.team_name != team_name:
            if team_name == "":
                raise serializers.ValidationError("Team name blank")
            if instance.team_name == "":
                raise serializers.ValidationError("Please join a Team first")
            if DiscordUser.objects.filter(team_name=team_name).count() > 0:
                raise serializers.ValidationError("Team name already taken")
            DiscordUser.objects.filter(team_name=instance.team_name).update(team_name=team_name)

    def create_team_name(self, instance, validated_data):
        team_name = validated_data.get('team_name', None)
        team_created = validated_data.get('team_created', False)
        if team_created and team_name is not None and instance.team_name != team_name:
            if team_name == "":
                raise serializers.ValidationError("Team name blank")
            if DiscordUser.objects.filter(team_name=team_name).count() > 0:
                raise serializers.ValidationError("Team name already taken")

    def append_stickers(self, instance, validated_data):
        sticker = validated_data.get('stickers', None)
        if sticker:
            stickers = instance.stickers.split('-')
            if sticker not in stickers:
                if instance.stickers:
                    instance.stickers = instance.stickers + '-' + sticker
                else:
                    instance.stickers = sticker
            else:
                raise serializers.ValidationError("Sticker already added")
            del validated_data['stickers']

    def update(self, instance, validated_data):
        self.change_team_name(instance, validated_data)
        self.create_team_name(instance, validated_data)
        self.append_stickers(instance, validated_data)
        return super().update(instance, validated_data)

    class Meta:
        model = DiscordUser
        fields = ['discord_id', 'checked_in', 'type', 'name', 'team_name', 'team_changed', 'team_created', 'stickers']
        read_only_fields = ['discord_id']
