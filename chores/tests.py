from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Household, HouseholdMember, ChoreDefinition, ChoreInstance
from .services import get_next_doer_and_inspector


class ModelTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user('alice', password='pass123')
        self.bob = User.objects.create_user('bob', password='pass123')
        self.house = Household.objects.create(name='Test House')
        HouseholdMember.objects.create(user=self.alice, household=self.house, rotation_order=1)
        HouseholdMember.objects.create(user=self.bob, household=self.house, rotation_order=2)
        self.chore_def = ChoreDefinition.objects.create(
            household=self.house, title='Dishes', frequency='WEEKLY'
        )

    def test_household_member_linked_correctly(self):
        member = HouseholdMember.objects.get(user=self.alice)
        self.assertEqual(member.household, self.house)

    def test_chore_instance_stores_separate_doer_and_inspector(self):
        instance = ChoreInstance.objects.create(
            chore_definition=self.chore_def,
            doer=self.alice,
            inspector=self.bob,
            start_date=date.today(),
            due_date=date.today() + timedelta(days=7),
        )
        self.assertEqual(instance.doer, self.alice)
        self.assertEqual(instance.inspector, self.bob)
        self.assertIn(instance, self.alice.assigned_tasks.all())
        self.assertIn(instance, self.bob.assigned_inspections.all())

    def test_default_status_is_pending(self):
        instance = ChoreInstance.objects.create(
            chore_definition=self.chore_def,
            doer=self.alice,
            inspector=self.bob,
            start_date=date.today(),
            due_date=date.today() + timedelta(days=7),
        )
        self.assertEqual(instance.status, 'PENDING')


class RotationEngineTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user('alice', password='pass123')
        self.bob = User.objects.create_user('bob', password='pass123')
        self.house = Household.objects.create(name='Test House')
        HouseholdMember.objects.create(user=self.alice, household=self.house, rotation_order=1)
        HouseholdMember.objects.create(user=self.bob, household=self.house, rotation_order=2)
        self.chore_def = ChoreDefinition.objects.create(
            household=self.house, title='Dishes', frequency='WEEKLY'
        )

    def test_first_assignment_with_no_current_doer(self):
        doer, inspector = get_next_doer_and_inspector(self.chore_def, current_doer=None)
        self.assertEqual(doer, self.alice)
        self.assertEqual(inspector, self.bob)

    def test_rotation_advances_to_next_member(self):
        doer, inspector = get_next_doer_and_inspector(self.chore_def, current_doer=self.alice)
        self.assertEqual(doer, self.bob)
        self.assertEqual(inspector, self.alice)

    def test_single_member_household_returns_same_user(self):
        solo_house = Household.objects.create(name='Solo House')
        solo_user = User.objects.create_user('solo', password='pass123')
        HouseholdMember.objects.create(user=solo_user, household=solo_house, rotation_order=1)
        solo_def = ChoreDefinition.objects.create(household=solo_house, title='Trash', frequency='WEEKLY')

        doer, inspector = get_next_doer_and_inspector(solo_def, current_doer=None)
        self.assertEqual(doer, solo_user)
        self.assertEqual(inspector, solo_user)

    def test_empty_household_raises_error(self):
        empty_house = Household.objects.create(name='Empty House')
        empty_def = ChoreDefinition.objects.create(household=empty_house, title='Nothing', frequency='WEEKLY')

        with self.assertRaises(ValueError):
            get_next_doer_and_inspector(empty_def, current_doer=None)


class DashboardViewTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user('alice', password='pass123')
        self.bob = User.objects.create_user('bob', password='pass123')
        self.house = Household.objects.create(name='Test House')
        HouseholdMember.objects.create(user=self.alice, household=self.house, rotation_order=1)
        HouseholdMember.objects.create(user=self.bob, household=self.house, rotation_order=2)
        self.chore_def = ChoreDefinition.objects.create(
            household=self.house, title='Dishes', frequency='WEEKLY'
        )
        self.instance = ChoreInstance.objects.create(
            chore_definition=self.chore_def,
            doer=self.alice,
            inspector=self.bob,
            status='PENDING',
            start_date=date.today(),
            due_date=date.today() + timedelta(days=7),
        )

    def test_logged_out_user_redirected_to_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_doer_sees_assigned_task(self):
        self.client.login(username='alice', password='pass123')
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, 'Dishes')

    def test_inspector_only_sees_tasks_needing_inspection(self):
        self.client.login(username='bob', password='pass123')
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, 'No pending inspections')

        self.instance.status = 'NEEDS_INSPECTION'
        self.instance.save()
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, 'Dishes')


class ChoreActionViewTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user('alice', password='pass123')
        self.bob = User.objects.create_user('bob', password='pass123')
        self.house = Household.objects.create(name='Test House')
        HouseholdMember.objects.create(user=self.alice, household=self.house, rotation_order=1)
        HouseholdMember.objects.create(user=self.bob, household=self.house, rotation_order=2)
        self.chore_def = ChoreDefinition.objects.create(
            household=self.house, title='Dishes', frequency='WEEKLY'
        )
        self.instance = ChoreInstance.objects.create(
            chore_definition=self.chore_def,
            doer=self.alice,
            inspector=self.bob,
            status='PENDING',
            start_date=date.today(),
            due_date=date.today() + timedelta(days=7),
        )

    def test_mark_complete_changes_status(self):
        self.client.login(username='alice', password='pass123')
        self.client.post(reverse('mark_chore_complete', args=[self.instance.pk]))
        self.instance.refresh_from_db()
        self.assertEqual(self.instance.status, 'NEEDS_INSPECTION')

    def test_approve_sets_status_approved(self):
        self.instance.status = 'NEEDS_INSPECTION'
        self.instance.save()
        self.client.login(username='bob', password='pass123')
        self.client.post(reverse('review_chore', args=[self.instance.pk]), {'action': 'approve'})
        self.instance.refresh_from_db()
        self.assertEqual(self.instance.status, 'APPROVED')

    def test_reject_sets_status_and_notes(self):
        self.instance.status = 'NEEDS_INSPECTION'
        self.instance.save()
        self.client.login(username='bob', password='pass123')
        self.client.post(
            reverse('review_chore', args=[self.instance.pk]),
            {'action': 'reject', 'rejection_notes': 'Missed a spot'}
        )
        self.instance.refresh_from_db()
        self.assertEqual(self.instance.status, 'REJECTED')
        self.assertEqual(self.instance.rejection_notes, 'Missed a spot')

    def test_non_inspector_cannot_review(self):
        self.client.login(username='alice', password='pass123')
        response = self.client.post(
            reverse('review_chore', args=[self.instance.pk]),
            {'action': 'approve'}
        )
        self.assertEqual(response.status_code, 404)