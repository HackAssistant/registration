import csv
import io

from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render

from app.utils import reverse
from app.views import TabsView
from judging import forms
from judging.models import Project, Presentation
from user.mixins import IsDirectorMixin, IsOrganizerMixin


def organizer_tabs(user):
    t = [('Judge', reverse('judge_projects'), False), ]
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


class RoomJudgingView(IsOrganizerMixin, TabsView):
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
            c.update({'room': self.request.user.room,
                      'project': project})
        return c

    pass
