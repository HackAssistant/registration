from django.urls import  reverse_lazy
from register.models import Application
from table import Table
from table.columns import Column
from table.columns import LinkColumn, Link
from table.utils import A


class ApplicationsTable(Table):
    id = Column(field='id', header='Id',sortable=False,)
    name = Column(field='name', header='Name',sortable=False,)
    lastname = Column(field='lastname', header='Lastname',sortable=False,)
    email = Column(field='email', header='Email',sortable=False,)
    checkin = LinkColumn(field='lastname', header='Checkin', sortable=False,
                         links=[Link(text=u'checkin', viewname='check_in_hacker', kwargs={'id': A('id')}), ])

    class Meta:
        model = Application
        search = True
