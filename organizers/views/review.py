# Create your views here.
import os
from io import BytesIO
from zipfile import ZipFile

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count, Q
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.utils import timezone
from datetime import timedelta

from app import slack
from app.mixins import TabsViewMixin
from app.slack import SlackInvitationException
from applications import emails
from applications.models import (
    APP_PENDING,
    APP_DUBIOUS,
    APP_BLACKLISTED,
    AcceptedResume,
    APP_ATTENDED,
)
from applications.validators import validate_file_extension_size
from organizers import models
from teams.models import Team
from user.mixins import (
    IsOrganizerMixin,
    HaveSponsorPermissionMixin,
    HaveMentorPermissionMixin,
)

from organizers.views.application_lists import hacker_tabs


def add_vote(application, user, tech_rat, pers_rat):
    """
    Save the vote of the application and
    if the number of votes is >= 5 and the CV is not flagged, create an AcceptedResume
    """
    v = models.Vote()
    v.user = user
    v.application = application
    v.tech = tech_rat
    v.personal = pers_rat
    v.save()
    votes_count = application.vote_set.count()
    if votes_count >= 5 and not application.cv_flagged:
        AcceptedResume.objects.update_or_create(
            application=application, defaults={"accepted": True}
        )
    return v


def add_comment(application, user, text):
    comment = models.ApplicationComment()
    comment.author = user
    comment.set_application(application)
    comment.text = text
    comment.save()
    return comment


def user_can_change_application_resume(user, application):
    if not application.is_dubious():
        return False
    return user.has_hx_access or user.has_dubious_access


def change_application_resume(request, application):
    resume = request.FILES.get("resume")
    if not resume:
        messages.error(request, "Please select a resume file")
        return False
    try:
        validate_file_extension_size(resume)
    except ValidationError as e:
        messages.error(request, "; ".join(e.messages))
        return False
    application.resume = resume
    application.save()
    add_comment(application, request.user, "Resume updated")
    messages.success(request, "Resume updated")
    return True


class ApplicationDetailView(TabsViewMixin, IsOrganizerMixin, TemplateView):
    template_name = "application_detail.html"

    def get_back_url(self):
        back = self.request.session.get("edit_app_back", "app_list")
        return reverse(back)

    def get_context_data(self, **kwargs):
        context = super(ApplicationDetailView, self).get_context_data(**kwargs)
        application = self.get_application(kwargs)
        context["app"] = application
        context["can_change_resume"] = bool(
            application
            and user_can_change_application_resume(self.request.user, application)
        )
        context["vote"] = self.can_vote()
        context["max_vote"] = dict(models.VOTES)
        if application:
            my_vote = (
                models.annotate_my_vote(
                    models.HackerApplication.objects.filter(pk=application.pk),
                    self.request.user,
                )
                .values_list("my_vote", flat=True)
                .first()
            )
            context["my_vote"] = dict(models.MY_VOTE_CHOICES).get(my_vote)
        if self.can_vote():
            context["apps_left_to_vote"] = (
                models.HackerApplication.objects.exclude(
                    vote__user_id=self.request.user.id
                )
                .filter(
                    status=APP_PENDING,
                    submission_date__lte=timezone.now() - timedelta(hours=2),
                )
                .count()
            )

        context["comments"] = models.ApplicationComment.objects.filter(
            hacker=application
        ).order_by("created_at")
        if (
            application
            and getattr(application.user, "team", False)
            and settings.TEAMS_ENABLED
        ):
            context["teammates"] = Team.objects.filter(
                team_code=application.user.team.team_code
            ).values("user__name", "user__email", "user")

            for mate in context["teammates"]:
                if application.user.id == mate["user"]:
                    mate["is_me"] = True
                    continue

                mate_app = models.HackerApplication.objects.filter(
                    user=mate["user"]
                ).first()
                if mate_app:
                    mate["app_uuid_str"] = mate_app.uuid_str

        return context

    def can_vote(self):
        return False

    def get_application(self, kwargs):
        application_id = kwargs.get("id", None)
        if not application_id:
            raise Http404
        application = models.HackerApplication.objects.filter(
            uuid=application_id
        ).first()
        if not application:
            raise Http404

        return application

    def post(self, request, *args, **kwargs):
        id_ = request.POST.get("app_id")
        application = models.HackerApplication.objects.get(pk=id_)

        comment_text = request.POST.get("comment_text", None)
        motive_of_ban = request.POST.get("motive_of_ban", None)
        dubious_type = request.POST.get("dubious_type", None)
        dubious_comment_text = request.POST.get("dubious_comment_text", None)

        if request.POST.get("add_comment"):
            add_comment(application, request.user, comment_text)
        elif request.POST.get("invite") and request.user.is_director:
            self.invite_application(application)
        elif request.POST.get("confirm") and request.user.is_director:
            self.confirm_application(application)
        elif request.POST.get("cancel") and request.user.is_director:
            self.cancel_application(application)
        elif request.POST.get("waitlist") and request.user.is_director:
            self.waitlist_application(application)
        elif request.POST.get("slack") and request.user.is_organizer:
            self.slack_invite(application)
        elif request.POST.get("set_dubious") and request.user.is_organizer:
            application.set_dubious(request.user, dubious_type, dubious_comment_text)
        elif request.POST.get("set_flagged_cv") and request.user.is_organizer:
            application.set_flagged_cv()
        elif request.POST.get("unset_flagged_cv") and request.user.is_organizer:
            application.unset_flagged_cv()
        elif request.POST.get("contact_user") and request.user.has_dubious_access:
            application.set_contacted(request.user)
        elif request.POST.get("unset_dubious") and request.user.has_dubious_access:
            add_comment(
                application,
                request.user,
                "Dubious review result: No problems, hacker allowed to participate in hackathon!",
            )
            application.unset_dubious()
        elif request.POST.get("invalidate") and request.user.has_dubious_access:
            add_comment(
                application,
                request.user,
                "Dubious review result: Hacker is not allowed to participate in hackathon.",
            )
            application.invalidate()
        elif request.POST.get("set_blacklist") and request.user.is_organizer:
            application.set_blacklist()
        elif request.POST.get("unset_blacklist") and request.user.has_blacklist_access:
            add_comment(
                application,
                request.user,
                "Blacklist review result: No problems, hacker allowed to participate in hackathon!",
            )
            application.unset_blacklist()
        elif (
            request.POST.get("confirm_blacklist") and request.user.has_blacklist_access
        ):
            add_comment(
                application,
                request.user,
                "Blacklist review result: Hacker is not allowed to participate in hackathon. "
                + "Motive of ban: "
                + motive_of_ban,
            )
            application.confirm_blacklist(request.user, motive_of_ban)
        elif request.POST.get("change_resume"):
            if user_can_change_application_resume(request.user, application):
                change_application_resume(request, application)
            else:
                messages.error(request, "You have no permissions to do this")

        return HttpResponseRedirect(
            reverse("app_detail", kwargs={"id": application.uuid_str})
        )

    def waitlist_application(self, application):
        try:
            application.reject()
            messages.success(
                self.request, "%s application wait listed" % application.user.email
            )
        except ValidationError as e:
            messages.error(self.request, e.message)

    def slack_invite(self, application):
        try:
            slack.send_slack_invite(application.user.email)
            messages.success(
                self.request, "Slack invite sent to %s" % application.user.email
            )
        except SlackInvitationException as e:
            messages.error(self.request, "Slack error: %s" % str(e))

    def cancel_application(self, application):
        try:
            application.cancel()
            messages.success(
                self.request, "%s application cancelled" % application.user.email
            )
        except ValidationError as e:
            messages.error(self.request, e.message)

    def confirm_application(self, application):
        try:
            application.confirm()
            messages.success(
                self.request, "Ticket to %s successfully sent" % application.user.email
            )
            m = emails.create_confirmation_email(application, self.request)
            if m:
                m.send()
        except ValidationError as e:
            messages.error(self.request, e.message)

    def invite_application(self, application):
        try:
            application.invite(self.request.user)
            messages.success(
                self.request, "Invite to %s successfully sent" % application.user.email
            )
            m = emails.create_invite_email(application, self.request)
            if m:
                m.send()
        except ValidationError as e:
            messages.error(self.request, e.message)


class ReviewApplicationView(ApplicationDetailView):
    def get_current_tabs(self):
        return hacker_tabs(self.request.user)

    def get_back_url(self):
        return None

    def get_application(self, kwargs):
        """
        Django model to the rescue. This is transformed to an SQL sentence
        that does exactly what we need
        :return: pending aplication that has not been voted by the current
        user and that has less votes and its older
        """
        max_votes_to_app = getattr(settings, "MAX_VOTES_TO_APP", 50)
        return (
            models.HackerApplication.objects.exclude(
                Q(vote__user_id=self.request.user.id) | Q(user_id=self.request.user.id)
            )
            .filter(status=APP_PENDING)
            .filter(submission_date__lte=timezone.now() - timedelta(hours=2))
            .annotate(count=Count("vote__calculated_vote"))
            .filter(count__lte=max_votes_to_app)
            .order_by("count", "submission_date")
            .first()
        )

    def get(self, request, *args, **kwargs):
        r = super(ReviewApplicationView, self).get(request, *args, **kwargs)
        return r

    def post(self, request, *args, **kwargs):
        tech_vote = request.POST.get("tech_rat", None)
        pers_vote = request.POST.get("pers_rat", None)
        comment_text = request.POST.get("comment_text", None)
        dubious_type = request.POST.get("dubious_type", None)
        dubious_comment_text = request.POST.get("dubious_comment_text", None)

        application = models.HackerApplication.objects.get(
            pk=request.POST.get("app_id")
        )
        try:
            if request.POST.get("skip"):
                add_vote(application, request.user, None, None)
            elif request.POST.get("add_comment"):
                add_comment(application, request.user, comment_text)
                return HttpResponseRedirect(
                    "/applications/hacker/review/" + application.uuid_str
                )
            elif request.POST.get("set_dubious"):
                application.set_dubious(
                    request.user, dubious_type, dubious_comment_text
                )
            elif request.POST.get("unset_dubious"):
                application.unset_dubious()
            elif request.POST.get("set_flagged_cv") and request.user.is_organizer:
                application.set_flagged_cv()
            elif request.POST.get("unset_flagged_cv") and request.user.is_organizer:
                application.unset_flagged_cv()
            elif request.POST.get("set_blacklist") and request.user.is_organizer:
                application.set_blacklist()
            elif (
                request.POST.get("unset_blacklist")
                and request.user.has_blacklist_access
            ):
                add_comment(
                    application,
                    request.user,
                    "Blacklist review result: No problems, hacker allowed to participate in hackathon!",
                )
                application.unset_blacklist()
            else:
                add_vote(application, request.user, tech_vote, pers_vote)
        # If application has already been voted -> Skip and bring next
        # application
        except IntegrityError:
            pass
        return HttpResponseRedirect(reverse("review"))

    def can_vote(self):
        return True


class ReviewApplicationDetailView(ApplicationDetailView):
    def get_current_tabs(self):
        return hacker_tabs(self.request.user)

    def get_back_url(self):
        return None

    def get_application(self, kwargs):
        """
        Django model to the rescue. This is transformed to an SQL sentence
        that does exactly what we need
        :return: pending aplication that has not been voted by the current
        user and that has less votes and its older
        """
        if "id" in kwargs:
            if (
                models.HackerApplication.objects.filter(uuid=kwargs["id"])
                .first()
                .status
                != APP_PENDING
            ):
                max_votes_to_app = getattr(settings, "MAX_VOTES_TO_APP", 50)
                return (
                    models.HackerApplication.objects.exclude(
                        Q(vote__user_id=self.request.user.id)
                        | Q(user_id=self.request.user.id)
                    )
                    .filter(status=APP_PENDING)
                    .filter(submission_date__lte=timezone.now() - timedelta(hours=2))
                    .annotate(count=Count("vote__calculated_vote"))
                    .filter(count__lte=max_votes_to_app)
                    .order_by("count", "submission_date")
                    .first()
                )
            else:
                return models.HackerApplication.objects.get(uuid=kwargs["id"])
        else:
            max_votes_to_app = getattr(settings, "MAX_VOTES_TO_APP", 50)
            return (
                models.HackerApplication.objects.exclude(
                    Q(vote__user_id=self.request.user.id)
                    | Q(user_id=self.request.user.id)
                )
                .filter(status=APP_PENDING)
                .filter(submission_date__lte=timezone.now() - timedelta(hours=2))
                .annotate(count=Count("vote__calculated_vote"))
                .filter(count__lte=max_votes_to_app)
                .order_by("count", "submission_date")
                .first()
            )

    def get(self, request, *args, **kwargs):
        r = super(ReviewApplicationDetailView, self).get(request, *args, **kwargs)
        return r

    def post(self, request, *args, **kwargs):
        tech_vote = request.POST.get("tech_rat", None)
        pers_vote = request.POST.get("pers_rat", None)
        comment_text = request.POST.get("comment_text", None)
        dubious_type = request.POST.get("dubious_type", None)
        dubious_comment_text = request.POST.get("dubious_comment_text", None)

        application = models.HackerApplication.objects.get(
            pk=request.POST.get("app_id")
        )
        try:
            if request.POST.get("skip"):
                add_vote(application, request.user, None, None)
            elif request.POST.get("add_comment"):
                add_comment(application, request.user, comment_text)
                return HttpResponseRedirect(
                    "/applications/hacker/review/" + application.uuid_str
                )
            elif request.POST.get("set_dubious"):
                application.set_dubious(
                    request.user, dubious_type, dubious_comment_text
                )
            elif request.POST.get("unset_dubious"):
                application.unset_dubious()
            elif request.POST.get("set_flagged_cv") and request.user.is_organizer:
                application.set_flagged_cv()
            elif request.POST.get("unset_flagged_cv") and request.user.is_organizer:
                application.unset_flagged_cv()
            elif request.POST.get("set_blacklist") and request.user.is_organizer:
                application.set_blacklist()
            elif (
                request.POST.get("unset_blacklist")
                and request.user.has_blacklist_access
            ):
                add_comment(
                    application,
                    request.user,
                    "Blacklist review result: No problems, hacker allowed to participate in hackathon!",
                )
                application.unset_blacklist()
            else:
                add_vote(application, request.user, tech_vote, pers_vote)
        # If application has already been voted -> Skip and bring next
        # application
        except IntegrityError:
            pass
        return HttpResponseRedirect(reverse("review"))

    def can_vote(self):
        return True


class ReviewVolunteerApplicationView(IsOrganizerMixin, TabsViewMixin, TemplateView):
    template_name = "other_application_detail.html"

    def get_application(self, kwargs):
        application_id = kwargs.get("id", None)
        if not application_id:
            raise Http404
        application = models.VolunteerApplication.objects.filter(
            uuid=application_id
        ).first()
        if not application:
            raise Http404

        return application

    def post(self, request, *args, **kwargs):
        id_ = request.POST.get("app_id")
        comment_text = request.POST.get("comment_text", None)
        application = models.VolunteerApplication.objects.get(pk=id_)
        if request.POST.get("invite") and request.user.is_organizer:
            application.invite(request.user)
            application.save()
            m = emails.create_invite_email(application, self.request)
            if m:
                m.send()
                messages.success(request, "Volunteer invited!")
        elif request.POST.get("reject") and request.user.is_organizer:
            application.reject()
            application.save()
        elif request.POST.get("cancel_invite") and request.user.is_organizer:
            application.move_to_pending()
            messages.success(request, "Volunteer invite canceled")
        elif request.POST.get("add_comment"):
            add_comment(application, request.user, comment_text)
            messages.success(request, "Comment added")
        elif request.POST.get("change_valid") and request.user.is_organizer:
            application.valid = not application.valid
            application.save()
            messages.success(request, "Volunteer valid status changed")

        return HttpResponseRedirect(
            reverse("volunteer_detail", kwargs={"id": application.uuid_str})
        )

    def get_back_url(self):
        return reverse("volunteer_list")

    def get_context_data(self, **kwargs):
        context = super(ReviewVolunteerApplicationView, self).get_context_data(**kwargs)
        application = self.get_application(kwargs)
        context["app"] = application
        context["comments"] = models.ApplicationComment.objects.filter(
            volunteer=application
        ).order_by("created_at")
        return context


class ReviewSponsorApplicationView(
    TabsViewMixin, HaveSponsorPermissionMixin, TemplateView
):
    template_name = "other_application_detail.html"

    def get_application(self, kwargs):
        application_id = kwargs.get("id", None)
        if not application_id:
            raise Http404
        application = models.SponsorApplication.objects.filter(
            uuid=application_id
        ).first()
        if not application:
            raise Http404

        return application

    def get_back_url(self):
        return reverse("sponsor_list")

    def post(self, request, *args, **kwargs):
        id_ = request.POST.get("app_id")
        comment_text = request.POST.get("comment_text", None)
        application = models.SponsorApplication.objects.get(pk=id_)
        if request.POST.get("add_comment"):
            add_comment(application, request.user, comment_text)
            messages.success(request, "Comment added")

        return HttpResponseRedirect(
            reverse("sponsor_detail", kwargs={"id": application.uuid_str})
        )

    def get_context_data(self, **kwargs):
        context = super(ReviewSponsorApplicationView, self).get_context_data(**kwargs)
        application = self.get_application(kwargs)
        context["app"] = application
        context["comments"] = models.ApplicationComment.objects.filter(
            sponsor=application
        ).order_by("created_at")
        return context


class ReviewMentorApplicationView(
    TabsViewMixin, HaveMentorPermissionMixin, TemplateView
):
    template_name = "other_application_detail.html"

    def get_application(self, kwargs):
        application_id = kwargs.get("id", None)
        if not application_id:
            raise Http404
        application = models.MentorApplication.objects.filter(
            uuid=application_id
        ).first()
        if not application:
            raise Http404

        return application

    def post(self, request, *args, **kwargs):
        id_ = request.POST.get("app_id")
        application = models.MentorApplication.objects.get(pk=id_)
        comment_text = request.POST.get("comment_text", None)
        if request.POST.get("invite") and request.user.is_organizer:
            application.invite(request.user)
            application.save()
            m = emails.create_invite_email(application, self.request)
            if m:
                m.send()
                messages.success(request, "Mentor invited!")
        elif request.POST.get("cancel_invite") and request.user.is_organizer:
            application.move_to_pending()
            messages.success(request, "Mentor invite canceled")
        elif request.POST.get("add_comment"):
            add_comment(application, request.user, comment_text)
            messages.success(request, "comment added")
        elif request.POST.get("change_valid") and request.user.is_organizer:
            application.valid = not application.valid
            application.save()
            messages.success(request, "Mentor valid status changed")

        return HttpResponseRedirect(
            reverse("mentor_detail", kwargs={"id": application.uuid_str})
        )

    def get_back_url(self):
        return reverse("mentor_list")

    def get_context_data(self, **kwargs):
        context = super(ReviewMentorApplicationView, self).get_context_data(**kwargs)
        application = self.get_application(kwargs)
        context["app"] = application
        context["comments"] = models.ApplicationComment.objects.filter(
            mentor=application
        ).order_by("created_at")
        return context


class ReviewResume(TabsViewMixin, HaveSponsorPermissionMixin, TemplateView):
    template_name = "review_resume.html"

    def get_current_tabs(self):
        return hacker_tabs(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app = (
            models.HackerApplication.objects.filter(
                acceptedresume__isnull=True, cv_flagged=True, resume__isnull=False
            )
            .exclude(status__in=[APP_DUBIOUS, APP_BLACKLISTED])
            .first()
        )
        context.update({"app": app})
        return context

    def post(self, request, *args, **kwargs):
        app_id = request.POST.get("app_id")
        accepted = request.POST.get("accepted")
        AcceptedResume(application_id=app_id, accepted=(accepted == "true")).save()
        return redirect(reverse("review_resume"))

    def get(self, request, *args, **kwargs):
        file = request.GET.get("files", False)
        if file:
            s = BytesIO()
            accepted_resumes = AcceptedResume.objects.filter(
                accepted=True, application__status__in=[APP_ATTENDED]
            ).select_related("application")
            with ZipFile(s, "w") as zip_file:
                for accepted_resume in accepted_resumes:
                    file_path = accepted_resume.application.resume.path
                    _, fname = os.path.split(file_path)
                    zip_path = os.path.join("resumes", fname)
                    zip_file.write(file_path, zip_path)
            resp = HttpResponse(
                s.getvalue(), content_type="application/x-zip-compressed"
            )
            resp["Content-Disposition"] = "attachment; filename=resumes.zip"
            return resp
        return super().get(request, *args, **kwargs)


class VisualizeResume(IsOrganizerMixin, TemplateView):
    template_name = "pdf_view.html"

    def get_application(self, kwargs):
        application_id = kwargs.get("id", None)
        if not application_id:
            raise Http404
        application = models.HackerApplication.objects.filter(
            uuid=application_id
        ).first()
        if not application:
            raise Http404
        return application

    def get_context_data(self, **kwargs):
        context = super(VisualizeResume, self).get_context_data(**kwargs)
        application = self.get_application(kwargs)
        context["app"] = application
        return context
