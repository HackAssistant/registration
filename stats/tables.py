from django_tables2 import tables

from user.models import User


class CheckinRankingListTable(tables.Table):
    class Meta:
        model = User
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['name', 'email', 'checkin_count']
        empty_text = 'No checked in user yet... Why? :\'('
        order_by = '-checkin_count'
