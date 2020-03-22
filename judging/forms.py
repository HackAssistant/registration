from django import forms
from django.conf import settings
from django.template.defaultfilters import filesizeformat
from form_utils.forms import BetterForm


class ProjectImportForm(BetterForm):
    projects_file = forms.FileField(required=True)

    def __init__(self, *args, **kwargs):
        super(ProjectImportForm, self).__init__(*args, **kwargs)
        self.fields['projects_file'].required = True

    def clean_projects_file(self):
        projects_file = self.cleaned_data['projects_file']
        size = getattr(projects_file, '_size', 0)
        if size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError("Please keep the filesize under %s. Current filesize %s" % (
                filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(size)))
        return projects_file

    def save(self, commit=True):
        print('im saving sth')
        pass

    # TODO: create dumb model for devpost data?
    #       with a field for the csv file (FileField)
    #       Alternative: process the file in-place
    #       and create all the project instances

    class Meta:
        fields = ('projects_file',)
        fieldsets = (('Upload the devpost CSV file with all the projects',
                      {'fields': ('projects_file',)}),)
        labels = {
            'projects_file': 'Devpost project collection (CSV)'
        }
