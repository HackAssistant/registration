from hackers.models import Application
from table import Table
from table.columns import Column
from table.columns import LinkColumn, Link
from table.utils import A


class ApplicationsListTable(Table):
    name = Column(field='hacker.name', header='Name', sortable=True, )
    lastname = Column(field='hacker.lastname', header='Lastname', sortable=True, )
    vote_avg = Column(field='vote_avg', header='Current valoration', searchable=False, visible=True)
    status = Column(field='get_status_display', header='Status', searchable=False)
    detail_link = LinkColumn(field='id', header='Detail', sortable=False, searchable=False,
                             links=[Link(text=u'Detail', viewname='app_detail', kwargs={'id': A('id')}), ])

    class Meta:
        sort = [(2, 'desc'), ]
        model = Application
        search = True
        zero_records = 'No applications'
