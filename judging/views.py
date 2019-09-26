import csv
import io

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from app import settings
from app.mixins import TabsViewMixin
from app.utils import reverse
from app.views import TabsView
from judging import forms
from judging.models import Project, Presentation, Room, PresentationEvaluation
from user.mixins import IsDirectorMixin


def organizer_tabs(user):
    t = [('Rooms', reverse('project_list'), False), ]
    if hasattr(user, 'room'):
        t.append(('Judge', reverse('judge_projects'), False))
    if user.is_director:
        t.append(('Import', reverse('import_projects'), False))
    return t


def handle_uploaded_projects(file):
    # TODO: write the file somewhere to store it?
    io_file = io.TextIOWrapper(file)
    reader = csv.DictReader(io_file)

    fieldnames_to_csv_cols = {
        'title': 'Submission Title',
        'url': 'Submission Url',
        'description': 'Plain Description',
        'video': 'Video',
        'website': 'Website',
        'file_url': 'File Url',
        'desired_prizes': 'Desired Prizes',
        'built_with': 'Built With',
        'submitter_screen_name': 'Submitter Screen Name',
        'submitter_first_name': 'Submitter First Name',
        'submitter_last_name': 'Submitter Last Name',
        'submitter_email': 'Submitter Email',
        'university': 'College/Universities Of Team Members',
        'additional_team_member_count': 'Additional Team Member Count'
    }

    for row in reader:
        # Create project instance
        data = {target: row[original] for target, original in fieldnames_to_csv_cols.items()}
        try:
            Project.objects.create(**data)
        except IntegrityError:
            pass

    projects = Project.objects.all()
    Presentation.objects.create_from_projects(projects)


class ImportProjectsView(IsDirectorMixin, TabsView):
    template_name = 'import_projects.html'

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_context_data(self, **kwargs):
        c = super(ImportProjectsView, self).get_context_data(**kwargs)
        form = forms.ProjectImportForm()
        c.update({'form': form})
        return c

    def post(self, request, *args, **kwargs):
        form = forms.ProjectImportForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_projects(request.FILES['projects_file'].file)
            messages.success(self.request, 'Your project file was successfully uploaded.')
        else:
            c = self.get_context_data()
            c.update({'form': form})
            return render(request, self.template_name, c)

        return HttpResponseRedirect(reverse('import_projects'))


def skip_presentation(presentation):
    presentation.turn = Presentation.objects.get_last_turn(presentation.room) + 1
    presentation.save()


class RoomJudgingView(TabsViewMixin, TemplateView):
    template_name = 'room_judging.html'

    def get_current_tabs(self):
        return organizer_tabs(self.request.user)

    def get_context_data(self, **kwargs):
        c = super(RoomJudgingView, self).get_context_data(**kwargs)
        if hasattr(self.request.user, 'room'):
            presentation = Presentation.objects.filter(
                room=self.request.user.room,
                done=False
            ).order_by('turn').first()
            project = presentation.project if presentation else None
            c.update({'presentation': presentation,
                      'room': self.request.user.room,
                      'project': project,
                      'is_global_challenge_room': presentation and presentation.room.challenge.name == settings.HACKATHON_NAME
                      })
        return c

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(self.request.user, 'room'):
            return redirect('project_list')
        else:
            return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(self.request.user, 'room'):
            return redirect_to_login(self.request.get_full_path())

        presentation_id = request.POST.get('presentation_id')
        presentation = Presentation.objects.get(pk=presentation_id)

        if presentation.room.challenge.name != settings.HACKATHON_NAME:
            if request.POST.get('skip'):
                skip_presentation(presentation)
            else:
                presentation.done = True
                presentation.save()

        judge_aliases = ['A', 'B', 'C']
        for judge in judge_aliases:
            tech = request.POST.get('tech_score_{}'.format(judge), None)
            design = request.POST.get('design_score_{}'.format(judge), None)
            completion = request.POST.get('completion_score_{}'.format(judge), None)
            learning = request.POST.get('learning_score_{}'.format(judge), None)

            try:
                if request.POST.get('skip'):
                    skip_presentation(presentation)
                elif request.POST.get('send'):
                    PresentationEvaluation.objects.get_or_create(
                        presentation=presentation,
                        judge_alias=judge,
                        tech=tech,
                        design=design,
                        completion=completion,
                        learning=learning
                    )
                    presentation.done = True
                    presentation.save()

            # If application has already been voted -> Skip and bring next
            # application
            except IntegrityError:
                pass
        return HttpResponseRedirect(reverse('judge_projects'))


class RoomsView(TemplateView):
    template_name = 'rooms_presentations.html'

    def get_context_data(self, **kwargs):
        c = super(RoomsView, self).get_context_data(**kwargs)
        c['rooms'] = Room.objects.all()
        """
        c['projects'] = {
            x.name: x.objects.get_current_presentations() for x in c['rooms']
        }
        """
        return c
