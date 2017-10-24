from table import Table
from table.columns import Column
from table.columns import LinkColumn, Link
from table.utils import A

from hackers.models import Application


class ApplicationsTable(Table):
    name = Column(field='hacker.name', header='Name', sortable=True, )
    lastname = Column(field='hacker.lastname', header='Lastname',
                      sortable=True, )
    email = Column(field='hacker.user.email', header='Email', sortable=True, )
    checkin = LinkColumn(field='id', header='Checkin', sortable=False,
                         links=[Link(text=u'checkin',
                                     viewname='check_in_hacker',
                                     kwargs={'id': A('id')}), ])

    class Meta:
        model = Application
        search = True
