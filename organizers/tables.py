from table import Table
from table.columns import Column
from table.columns import LinkColumn, Link
from table.utils import A

from hackers.models import Application


class ApplicationsListTable(Table):
    nickname = Column(field='user.nickname', header='Nickname', sortable=True, )
    email = Column(field='user.email', header='Email', sortable=True, )
    vote_avg = Column(field='vote_avg', header='Current valoration', searchable=False, visible=True)
    status = Column(field='get_status_display', header='Status', searchable=False)
    detail_link = LinkColumn(field='id', header='Detail', sortable=False, searchable=False,
                             links=[Link(text=u'Detail', viewname='app_detail', kwargs={'id': A('uuid_str')}), ])

    class Meta:
        sort = [(2, 'desc'), ]
        model = Application
        search = True
        zero_records = 'No applications'
