from django import forms
from django.conf import settings

from teams.models import Team


class JoinTeamForm(forms.ModelForm):
    def clean_team_code(self):
        team_code = self.cleaned_data['team_code']
        teammates = Team.objects.filter(team_code=team_code).count()
        if teammates == 0:
            raise forms.ValidationError("No team exists with the current code. Did you want to create a team instead?")
        max_teammates = getattr(settings, 'HACKATHON_MAX_TEAMMATES', 4)
        if teammates == max_teammates:
            raise forms.ValidationError("Full team. Max teammates is %d" % max_teammates)
        return team_code

    class Meta:
        model = Team
        exclude = ['user', ]
        labels = {
            'team_code': 'Your team code'
        }
        help_texts = {
            'team_code': 'Paste here the team code that your teammate has sent you'
        }
