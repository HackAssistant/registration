import django_tables2 as tables

from user.models import User


class CheckinRankingListTable(tables.Table):
    class Meta:
        model = User
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['name', 'email', 'checkin_count']
        empty_text = 'No checked in user yet... Why? :\'('
        order_by = '-checkin_count'


class OrganizerRankingListTable(tables.Table):
    counter = tables.TemplateColumn('{{ row_counter|add:1 }}', verbose_name='Position', orderable=False)

    class Meta:
        model = User
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['counter', 'email', 'vote_count', 'skip_count', 'total_count']
        empty_text = 'No organizers voted yet... Why? :\'('
        order_by = '-total_count'
