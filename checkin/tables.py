from models import CheckIn
from register.models import Application

from table import Table
from table.columns import Column
from table.columns import LinkColumn, Link
from table.utils import A

class ApplicationsTable(Table):
    id = Column(field='id', header='Id')
    name = Column(field='name', header='Name')
    lastname = Column(field='lastname', header='Lastname')
    checkin = LinkColumn(field='lastname', header='Checkin', links=[Link(text=u'checkin', viewname='check_in_hacker', args=(A('id'),),)])
    class Meta:
        model = Application
        search = True
        ajax = True
        a