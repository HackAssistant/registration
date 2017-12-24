from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render

from app.utils import hacker_tabs, reverse
from app.views import TabsView
from teams import forms
from teams import models


class HackerTeam(LoginRequiredMixin, TabsView):
    template_name = 'team.html'

    def get_current_tabs(self):
        return hacker_tabs(self.request.user)

    def get_context_data(self, **kwargs):
        c = super(HackerTeam, self).get_context_data(**kwargs)
        team = getattr(self.request.user, 'team', None)
        teammates = []
        if team:
            teammates = models.Team.objects.filter(team_code=team.team_code) \
                .values('user__name', 'user__email', 'user__application')
            teammates = list(map(lambda x:
                                 {'name': x['user__name'], 'email': x['user__email'], 'app': x['user__application']},
                                 teammates))
        instance = models.Team()
        instance.team_code = ''
        form = forms.JoinTeamForm(instance=instance)
        c.update({'team': team, 'teammates': teammates, 'form': form})
        return c

    def post(self, request, *args, **kwargs):

        if request.POST.get('create', None):
            team = models.Team()
            team.user = request.user
            team.save()
            return HttpResponseRedirect(reverse('teams'))
        if request.POST.get('leave', None):
            team = getattr(request.user, 'team', None)
            if team:
                team.delete()
            return HttpResponseRedirect(reverse('teams'))
        else:
            form = forms.JoinTeamForm(request.POST, request.FILES)
            if form.is_valid():
                team = form.save(commit=False)
                team.user = request.user
                team.save()

                messages.success(request, 'Team joined successfully!')

                return HttpResponseRedirect(reverse('teams'))
            else:
                c = self.get_context_data()
                c.update({'form': form})
                return render(request, self.template_name, c)
