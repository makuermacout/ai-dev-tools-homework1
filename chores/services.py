from .models import HouseholdMember


def get_next_doer_and_inspector(chore_definition, current_doer=None):
    """Calculates the next Doer and Inspector based on rotation order."""
    members = list(
        HouseholdMember.objects.filter(household=chore_definition.household)
        .order_by('rotation_order')
        .select_related('user')
    )

    if not members:
        raise ValueError("Household has no assigned members.")

    if len(members) == 1:
        # Single member housemate edge case
        return members[0].user, members[0].user

    if current_doer is None:
        # Default starting positions
        doer = members[0].user
        inspector = members[1].user
    else:
        # Locate index of current doer
        current_index = next(
            (i for i, m in enumerate(members) if m.user == current_doer), 0
        )
        
        # Advance doer to next position
        next_doer_index = (current_index + 1) % len(members)
        # Inspector is offset by 1 position ahead of doer
        next_inspector_index = (next_doer_index + 1) % len(members)

        doer = members[next_doer_index].user
        inspector = members[next_inspector_index].user

    return doer, inspector