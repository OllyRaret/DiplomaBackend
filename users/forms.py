from django import forms

from reference.stages import StartupStage
from .models import InvestorProfile


class InvestorProfileForm(forms.ModelForm):
    preferred_stages = forms.MultipleChoiceField(
        choices=StartupStage.CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label='Предпочтительные стадии инвестирования',
        required=False,
    )

    class Meta:
        model = InvestorProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs and kwargs['instance']:
            instance = kwargs['instance']
            initial = kwargs.get('initial', {})
            initial['preferred_stages'] = instance.preferred_stages
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    def clean_preferred_stages(self):
        return self.cleaned_data['preferred_stages']
