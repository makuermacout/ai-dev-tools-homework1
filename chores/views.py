from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import UserRegistrationForm, HouseholdForm
from .models import Household, HouseholdMember, ChoreInstance

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('create_or_join_household')
    else:
        form = UserRegistrationForm()
    return render(request, 'chores/register.html', {'form': form})


@login_required
def create_or_join_household(request):
    if hasattr(request.user, 'householdmember'):
        return redirect('dashboard')  # Redirect if user is already in a household

    if request.method == 'POST':
        household_id = request.POST.get('household_id')
        if household_id:
            # Join existing household
            household = Household.objects.get(id=household_id)
        else:
            # Create new household
            form = HouseholdForm(request.POST)
            if form.is_valid():
                household = form.save()

        # Calculate rotation order position
        member_count = HouseholdMember.objects.filter(household=household).count()
        HouseholdMember.objects.create(
            user=request.user,
            household=household,
            rotation_order=member_count + 1
        )
        return redirect('dashboard')

    households = Household.objects.all()
    form = HouseholdForm()
    return render(request, 'chores/setup_household.html', {
        'form': form,
        'households': households
    })



@login_required
def dashboard(request):
    user = request.user

    assigned_tasks = ChoreInstance.objects.filter(
        doer=user,
        status__in=['PENDING', 'REJECTED']
    ).select_related('chore_definition')

    inspections_pending = ChoreInstance.objects.filter(
        inspector=user,
        status='NEEDS_INSPECTION'
    ).select_related('chore_definition', 'doer')

    return render(request, 'chores/dashboard.html', {
        'assigned_tasks': assigned_tasks,
        'inspections_pending': inspections_pending,
    })


@login_required
def mark_chore_complete(request, pk):
    instance = get_object_or_404(ChoreInstance, pk=pk, doer=request.user)
    if request.method == 'POST':
        instance.status = 'NEEDS_INSPECTION'
        instance.completed_at = timezone.now()
        instance.save()
    return redirect('dashboard')


@login_required
def review_chore(request, pk):
    instance = get_object_or_404(ChoreInstance, pk=pk, inspector=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('rejection_notes', '')

        if action == 'approve':
            instance.status = 'APPROVED'
            instance.inspected_at = timezone.now()
        elif action == 'reject':
            instance.status = 'REJECTED'
            instance.rejection_notes = notes

        instance.save()
    return redirect('dashboard')