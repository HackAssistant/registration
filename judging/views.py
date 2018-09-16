import csv
import io

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render

from app.utils import reverse
from app.views import TabsView
from judging import forms
from user.mixins import IsDirectorMixin


def organizer_tabs(user):
    t = [('Projects', reverse('import_projects'), False), ]
#    t = [('Projects', reverse('project_list')), ]
    if user.is_director:
        t.append(('Import', reverse('import_projects'), False))
    return t


def handle_uploaded_projects(file):
    # TODO: write the file somewhere to store it?
    io_file = io.TextIOWrapper(file)
    reader = csv.DictReader(io_file)
    print(reader.fieldnames)

    for row in reader:
        # Create project instance
        # p = Project.objects.create(row)
        pass


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
            messages.success(self.request, 'Your project file was successfully uploaded.')
            handle_uploaded_projects(request.FILES['projects_file'].file)
        else:
            c = self.get_context_data()
            c.update({'form': form})
            return render(request, self.template_name, c)

        return HttpResponseRedirect(reverse('import_projects'))
