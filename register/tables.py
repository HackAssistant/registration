from register.models import Application
from table import Table
from table.columns import Column
from table.columns import LinkColumn, Link
from table.utils import A


class ApplicationsReviewTable(Table):
    name = Column(field='hacker.name', header='Name', sortable=True, )
    lastname = Column(field='hacker.lastname', header='Lastname', sortable=True, )
    email = Column(field='hacker.user.email', header='Email', sortable=True, )
    reviewLink = LinkColumn(field='id', header='Review', sortable=False,
                            links=[Link(text=u'Review', viewname='app_detail', kwargs={'id': A('id')}), ])


    class Meta:
        model = Application
        search = True
