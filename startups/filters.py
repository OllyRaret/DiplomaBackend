def filter_startups_for_specialist(queryset, params):
    industry = params.get('industry')
    stage = params.get('stage')
    required_profession = params.get('required_profession')
    required_skills = params.getlist('required_skills')

    if industry:
        queryset = queryset.filter(industry_id=industry)

    if stage:
        queryset = queryset.filter(stage=stage)

    if required_profession:
        queryset = queryset.filter(required_specialists__profession_id=required_profession)

    if required_skills:
        for skill_id in required_skills:
            queryset = queryset.filter(required_specialists__skills__id=skill_id)

    return queryset.distinct()


def filter_startups_for_investor(queryset, params):
    industry = params.get('industry')
    stage = params.get('stage')
    investment_needed_min = params.get('investment_needed_min')
    investment_needed_max = params.get('investment_needed_max')

    if industry:
        queryset = queryset.filter(industry_id=industry)

    if stage:
        queryset = queryset.filter(stage=stage)

    if investment_needed_min:
        queryset = queryset.filter(investment_needed__gte=investment_needed_min)

    if investment_needed_max:
        queryset = queryset.filter(investment_needed__lte=investment_needed_max)

    return queryset.distinct()
