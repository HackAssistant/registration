from django.http import HttpResponseRedirect

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
        return HttpResponseRedirect(reverse('import_projects'))
