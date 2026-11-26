from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import View
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from django_tables2.export import ExportMixin
from django.utils import timezone
from datetime import timedelta

from app.mixins import TabsViewMixin
from applications import emails
from applications.emails import send_batch_emails
from applications.models import (
    APP_PENDING,
    APP_DUBIOUS,
    APP_BLACKLISTED,
    APP_INVITED,
    APP_LAST_REMIDER,
    APP_CONFIRMED,
    APP_REJECTED,
)
from organizers import models
from organizers.tables import (
    ApplicationsListTable,
    HackerApplicationFilter,
    AdminApplicationsListTable,
    InviteFilter,
    DubiousListTable,
    DubiousApplicationFilter,
    VolunteerFilter,
    VolunteerListTable,
    MentorListTable,
    MentorFilter,
    SponsorListTable,
    SponsorFilter,
    SponsorUserListTable,
    SponsorUserFilter,
    BlacklistListTable,
    BlacklistApplicationFilter,
)
from user.mixins import (
    IsOrganizerMixin,
    IsDirectorMixin,
    HaveDubiousPermissionMixin,
    HaveSponsorPermissionMixin,
    HaveMentorPermissionMixin,
    IsBlacklistAdminMixin,
)
from user.models import User, USR_SPONSOR

if getattr(settings, "REIMBURSEMENT_ENABLED", False):
    from reimbursement.models import Reimbursement, RE_PEND_APPROVAL


def hacker_tabs(user):
    new_app = models.HackerApplication.objects.exclude(vote__user_id=user.id).filter(
        status=APP_PENDING, submission_date__lte=timezone.now() - timedelta(hours=2)
    )
    t = [
        ("Application", reverse("app_list"), False),
        ("Review", reverse("review"), "new" if new_app else ""),
    ]
    if user.has_dubious_access and getattr(settings, "DUBIOUS_ENABLED", False):
        t.append(
            (
                "Dubious",
                reverse("dubious"),
                (
                    "new"
                    if models.HackerApplication.objects.filter(
                        status=APP_DUBIOUS, contacted=False
                    ).count()
                    else ""
                ),
            )
        )
    if user.has_blacklist_access and getattr(settings, "BLACKLIST_ENABLED", False):
        t.append(
            (
                "Blacklist",
                reverse("blacklist"),
                (
                    "new"
                    if models.HackerApplication.objects.filter(
                        status=APP_BLACKLISTED, contacted=False
                    ).count()
                    else ""
                ),
            )
        )
    t.append(("Check-in", reverse("check_in_list"), False))
    if user.has_reimbursement_access:
        t.extend(
            [
                ("Reimbursements", reverse("reimbursement_list"), False),
                (
                    "Receipts",
                    reverse("receipt_review"),
                    (
                        "new"
                        if Reimbursement.objects.filter(status=RE_PEND_APPROVAL).count()
                        else False
                    ),
                ),
            ]
        )
    if user.has_sponsor_access:
        new_resume = (
            models.HackerApplication.objects.filter(
                acceptedresume__isnull=True, cvs_edition=True
            )
            .exclude(status__in=[APP_DUBIOUS, APP_BLACKLISTED])
            .first()
        )
        t.append(
            ("Review resume", reverse("review_resume"), "new" if new_resume else "")
        )
    return t


def sponsor_tabs(user):
    return [
        ("Users", reverse("sponsor_user_list"), False),
        ("Application", reverse("sponsor_list"), False),
        ("Check-in", reverse("check_in_sponsor_list"), False),
    ]


def volunteer_tabs(user):
    return [
        ("Application", reverse("volunteer_list"), False),
        ("Check-in", reverse("check_in_volunteer_list"), False),
    ]


def mentor_tabs(user):
    return [
        ("Application", reverse("mentor_list"), False),
        ("Check-in", reverse("check_in_mentor_list"), False),
    ]


class ApplicationsListView(
    TabsViewMixin, IsOrganizerMixin, ExportMixin, SingleTableMixin, FilterView
):
    template_name = "applications_list.html"
    table_class = ApplicationsListTable
    filterset_class = HackerApplicationFilter
    table_pagination = {"per_page": 100}
    exclude_columns = ("detail", "status", "vote_avg", "my_vote")
    export_name = "applications"

    def get(self, request, *args, **kwargs):
        request.session["edit_app_back"] = "app_list"
        return super().get(request, *args, **kwargs)

    def get_current_tabs(self):
        return hacker_tabs(self.request.user)

    def get_queryset(self):
        return models.annotate_my_vote(
            models.HackerApplication.annotate_vote(
                models.HackerApplication.objects.all()
            ),
            self.request.user,
        )

    def get_context_data(self, **kwargs):
        context = super(ApplicationsListView, self).get_context_data(**kwargs)
        context["otherApplication"] = False
        list_email = ""
        for u in context.get("object_list").values_list("user__email", flat=True):
            list_email += "%s, " % u
        context["emails"] = list_email
        return context


class InviteListView(TabsViewMixin, IsDirectorMixin, SingleTableMixin, FilterView):
    template_name = "invite_list.html"
    table_class = AdminApplicationsListTable
    filterset_class = InviteFilter
    table_pagination = {"per_page": 100}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        n_invited_hackers_today = models.HackerApplication.objects.filter(
            status=APP_INVITED,
            online=False,
            status_update_date__date=timezone.now().date(),
        ).count()

        n_waitlisted_hackers = models.HackerApplication.objects.filter(
            status=APP_REJECTED, online=False
        ).count()
        n_live_hackers = models.HackerApplication.objects.filter(
            status__in=[APP_INVITED, APP_LAST_REMIDER, APP_CONFIRMED], online=False
        ).count()

        context.update(
            {
                "n_live_hackers": n_live_hackers,
                "n_live_per_hackers": n_live_hackers
                * 100
                / getattr(settings, "N_MAX_LIVE_HACKERS", 0),
                "n_waitlisted_hackers": n_waitlisted_hackers,
                "n_invited_hackers_today": n_invited_hackers_today,
            }
        )

        return context

    def get_current_tabs(self):
        return hacker_tabs(self.request.user)

    def get_queryset(self):
        return models.HackerApplication.annotate_vote(
            models.HackerApplication.objects.filter(
                status__in=[APP_PENDING, APP_REJECTED]
            )
        ).order_by("-vote_avg")

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist("selected")
        apps = models.HackerApplication.objects.filter(pk__in=ids).all()
        mails = []
        errors = 0
        for app in apps:
            try:
                app.invite(
                    request.user,
                    online=request.POST.get("force_online", "false") == "true",
                )
                m = emails.create_invite_email(app, request)
                if m:
                    mails.append(m)
            except ValidationError:
                errors += 1
        if mails:
            send_batch_emails(mails)
            messages.success(request, "%s applications invited" % len(mails))
        else:
            errorMsg = "No applications invited"
            if errors != 0:
                errorMsg = "%s applications not invited" % errors
            messages.error(request, errorMsg)

        return HttpResponseRedirect(reverse("invite_list"))


class WaitlistedApplicationsListView(
    IsDirectorMixin, ExportMixin, SingleTableMixin, View
):
    # This view is to send all hacker applications left under_review to waitlisted
    def post(self, request, *args, **kwargs):
        models.HackerApplication.objects.filter(status=APP_PENDING).update(
            status=APP_REJECTED
        )
        return HttpResponse(status=200)


class DubiousApplicationsListView(
    TabsViewMixin, HaveDubiousPermissionMixin, ExportMixin, SingleTableMixin, FilterView
):
    template_name = "dubious_list.html"
    table_class = DubiousListTable
    filterset_class = DubiousApplicationFilter
    table_pagination = {"per_page": 100}
    exclude_columns = ("status", "vote_avg")
    export_name = "dubious_applications"

    def get(self, request, *args, **kwargs):
        request.session["edit_app_back"] = "dubious"
        return super().get(request, *args, **kwargs)

    def get_current_tabs(self):
        return hacker_tabs(self.request.user)

    def get_queryset(self):
        return models.HackerApplication.objects.filter(status=APP_DUBIOUS).order_by(
            "-status_update_date"
        )


class BlacklistApplicationsListView(
    TabsViewMixin, IsBlacklistAdminMixin, ExportMixin, SingleTableMixin, FilterView
):
    template_name = "blacklist_list.html"
    table_class = BlacklistListTable
    filterset_class = BlacklistApplicationFilter
    table_pagination = {"per_page": 100}
    exclude_columns = ("status", "vote_avg")
    export_name = "blacklist_applications"

    def get(self, request, *args, **kwargs):
        request.session["edit_app_back"] = "blacklist"
        return super().get(request, *args, **kwargs)

    def get_current_tabs(self):
        return hacker_tabs(self.request.user)

    def get_queryset(self):
        return models.HackerApplication.objects.filter(status=APP_BLACKLISTED)


class _OtherApplicationsListView(
    TabsViewMixin, ExportMixin, SingleTableMixin, FilterView
):
    template_name = "applications_list.html"
    table_pagination = {"per_page": 100}
    exclude_columns = ("detail", "status")
    export_name = "applications"
    email_field = "user__email"

    def get_context_data(self, **kwargs):
        context = super(_OtherApplicationsListView, self).get_context_data(**kwargs)
        context["otherApplication"] = True
        list_email = ""
        for u in context.get("object_list").values_list(self.email_field, flat=True):
            list_email += "%s, " % u
        context["emails"] = list_email
        return context


class VolunteerApplicationsListView(IsOrganizerMixin, _OtherApplicationsListView):
    table_class = VolunteerListTable
    filterset_class = VolunteerFilter

    def get_queryset(self):
        return models.VolunteerApplication.objects.all()

    def get_current_tabs(self):
        return volunteer_tabs(self.request.user)


class SponsorApplicationsListView(
    HaveSponsorPermissionMixin, _OtherApplicationsListView
):
    table_class = SponsorListTable
    filterset_class = SponsorFilter
    email_field = "email"

    def get_queryset(self):
        return models.SponsorApplication.objects.all()

    def get_context_data(self, **kwargs):
        context = super(SponsorApplicationsListView, self).get_context_data(**kwargs)
        context["otherApplication"] = True
        return context

    def get_current_tabs(self):
        return sponsor_tabs(self.request.user)


class SponsorUserListView(
    HaveSponsorPermissionMixin, TabsViewMixin, ExportMixin, SingleTableMixin, FilterView
):
    template_name = "applications_list.html"
    table_pagination = {"per_page": 100}
    exclude_columns = ("detail", "status")
    export_name = "applications"
    table_class = SponsorUserListTable
    filterset_class = SponsorUserFilter

    def get_current_tabs(self):
        return sponsor_tabs(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(SponsorUserListView, self).get_context_data(**kwargs)
        context["otherApplication"] = True
        context["createUser"] = True
        return context

    def get_queryset(self):
        return User.objects.filter(type=USR_SPONSOR).exclude(max_applications=0)


class MentorApplicationsListView(HaveMentorPermissionMixin, _OtherApplicationsListView):
    table_class = MentorListTable
    filterset_class = MentorFilter

    def get_queryset(self):
        return models.MentorApplication.objects.all()

    def get_current_tabs(self):
        return mentor_tabs(self.request.user)
