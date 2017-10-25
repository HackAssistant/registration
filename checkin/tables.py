from table import Table
from table.columns import Column
from table.columns import LinkColumn, Link
from table.utils import A

from hackers.models import Application


class ApplicationsTable(Table):
    nickname = Column(field='user.nickname', header='Name', sortable=True, )
    email = Column(field='user.email', header='Email', sortable=True, )
    checkin = LinkColumn(field='id', header='Checkin', sortable=False,
                         links=[Link(text=u'checkin',
                                     viewname='check_in_hacker',
                                     kwargs={'id': A('uuid_str')}), ])

    class Meta:
        model = Application
        search = True
