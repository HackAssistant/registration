import pytest
from django.urls import reverse

from applications.models import APP_BLACKLISTED, APP_DUBIOUS, APP_INVITED, APP_PENDING, APP_REJECTED
from applications.models.hacker import HackerApplication
from organizers.models import MY_VOTE_NONE, MY_VOTE_SKIPPED, MY_VOTE_VOTED, Vote
from tests.factories import (
    HackerApplicationFactory,
    MentorApplicationFactory,
    OrganizerUserFactory,
    SponsorApplicationFactory,
    VolunteerApplicationFactory,
)


@pytest.fixture
def director_client(client, director_user):
    client.force_login(director_user)
    return client, director_user


@pytest.mark.django_db
def test_organizer_can_view_application_list(organizer_client):
    client, organizer = organizer_client
    app = HackerApplicationFactory()

    response = client.get(reverse("app_list"))

    assert response.status_code == 200
    assert app.user.email in response.context["emails"]


@pytest.mark.django_db
def test_hacker_cannot_view_application_list(hacker_client):
    client, hacker = hacker_client

    response = client.get(reverse("app_list"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_organizer_can_view_volunteer_list(organizer_client):
    client, organizer = organizer_client
    VolunteerApplicationFactory()

    response = client.get(reverse("volunteer_list"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_director_can_view_invite_list(director_client):
    client, director = director_client
    HackerApplicationFactory(status=APP_PENDING)
    HackerApplicationFactory(status=APP_INVITED)

    response = client.get(reverse("invite_list"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_organizer_cannot_view_invite_list(organizer_client):
    client, organizer = organizer_client

    response = client.get(reverse("invite_list"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_director_can_batch_invite(director_client):
    client, director = director_client
    app = HackerApplicationFactory(status=APP_PENDING)

    response = client.post(reverse("invite_list"), data={"selected": [str(app.pk)]})

    app.refresh_from_db()
    assert response.status_code == 302
    assert app.status == APP_INVITED


@pytest.mark.django_db
def test_director_can_waitlist_all_pending(director_client):
    client, director = director_client
    app = HackerApplicationFactory(status=APP_PENDING)

    response = client.post(reverse("waitlisted"))

    app.refresh_from_db()
    assert response.status_code == 200
    assert app.status == APP_REJECTED


@pytest.mark.django_db
def test_director_can_view_dubious_list(director_client):
    client, director = director_client
    HackerApplication.objects.filter(pk=HackerApplicationFactory().pk).update(status=APP_DUBIOUS)

    response = client.get(reverse("dubious"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_director_can_view_blacklist(director_client):
    client, director = director_client
    HackerApplication.objects.filter(pk=HackerApplicationFactory().pk).update(status=APP_BLACKLISTED)

    response = client.get(reverse("blacklist"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_director_can_view_mentor_list(director_client):
    client, director = director_client
    MentorApplicationFactory()

    response = client.get(reverse("mentor_list"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_director_can_view_sponsor_list(director_client):
    client, director = director_client
    SponsorApplicationFactory()

    response = client.get(reverse("sponsor_list"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_director_can_view_sponsor_user_list(director_client):
    client, director = director_client

    response = client.get(reverse("sponsor_user_list"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_director_can_view_mentor_detail(director_client):
    client, director = director_client
    app = MentorApplicationFactory()

    response = client.get(reverse("mentor_detail", kwargs={"id": app.uuid_str}))

    assert response.status_code == 200


@pytest.mark.django_db
def test_director_can_view_volunteer_detail(director_client):
    client, director = director_client
    app = VolunteerApplicationFactory()

    response = client.get(reverse("volunteer_detail", kwargs={"id": app.uuid_str}))

    assert response.status_code == 200


@pytest.mark.django_db
def test_director_can_invite_volunteer(director_client):
    client, director = director_client
    app = VolunteerApplicationFactory()

    response = client.post(
        reverse("volunteer_detail", kwargs={"id": app.uuid_str}), data={"app_id": str(app.pk), "invite": "true"}
    )

    app.refresh_from_db()
    assert response.status_code == 302
    assert app.status == APP_INVITED


@pytest.mark.django_db
def test_application_list_shows_my_vote(organizer_client):
    client, organizer = organizer_client
    voted = HackerApplicationFactory()
    skipped = HackerApplicationFactory()
    voted_by_other = HackerApplicationFactory()
    Vote.objects.create(application=voted, user=organizer, tech=4, personal=3)
    Vote.objects.create(application=skipped, user=organizer, tech=None, personal=None)
    Vote.objects.create(application=voted_by_other, user=OrganizerUserFactory(), tech=4, personal=3)

    response = client.get(reverse("app_list"))

    my_votes = {row.record.pk: row.record.my_vote for row in response.context["table"].rows}
    assert response.status_code == 200
    assert my_votes == {voted.pk: MY_VOTE_VOTED, skipped.pk: MY_VOTE_SKIPPED, voted_by_other.pk: MY_VOTE_NONE}


@pytest.mark.django_db
def test_application_list_filters_not_voted_by_me(organizer_client):
    client, organizer = organizer_client
    voted = HackerApplicationFactory()
    not_voted = HackerApplicationFactory()
    Vote.objects.create(application=voted, user=organizer, tech=4, personal=3)

    response = client.get(reverse("app_list"), {"my_vote": MY_VOTE_NONE})

    assert response.status_code == 200
    assert [row.record.pk for row in response.context["table"].rows] == [not_voted.pk]


@pytest.mark.django_db
def test_application_detail_shows_my_vote(organizer_client):
    client, organizer = organizer_client
    app = HackerApplicationFactory()
    Vote.objects.create(application=app, user=organizer, tech=4, personal=3)

    response = client.get(reverse("app_detail", kwargs={"id": app.uuid_str}))

    assert response.status_code == 200
    assert response.context["my_vote"] == "Voted"
