from django.contrib.auth import get_user_model
from django import forms
from .models import Parent, Child, Club, Enrollment, Session


class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address']


class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['first_name', 'last_name', 'child_age', 'school', 'classroom']


class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name']


User = get_user_model()


class SimpleDateWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        years = [(i, i) for i in range(2022, 2030)]
        months = [
            (1, 'Sausis'),
            (2, 'Vasaris'),
            (3, 'Kovas'),
            (4, 'Balandis'),
            (5, 'Gegužė'),
            (6, 'Birželis'),
            (7, 'Liepa'),
            (8, 'Rugpjūtis'),
            (9, 'Rugsėjis'),
            (10, 'Spalis'),
            (11, 'Lapkritis'),
            (12, 'Gruodis')
        ]
        days = [(i, i) for i in range(1, 32)]

        _widgets = [
            forms.Select(attrs=attrs, choices=years),
            forms.Select(attrs=attrs, choices=months),
            forms.Select(attrs=attrs, choices=days),
        ]
        super().__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            year, month, day = value.split('-')
            return [int(year), int(month), int(day)]
        return [None, None, None]

    def format_output(self, rendered_widgets):
        return '/'.join(rendered_widgets)

    def value_from_datadict(self, data, files, name):
        year_value = data.get('%s_0' % name)
        month_value = data.get('%s_1' % name)
        day_value = data.get('%s_2' % name)

        if year_value and month_value and day_value:
            return '%s-%s-%s' % (year_value, month_value, day_value)
        return None


class EnrollmentForm(forms.ModelForm):
    child = forms.ModelChoiceField(queryset=Child.objects.none(), empty_label="Pasirinkite vaiką")
    session = forms.ModelChoiceField(queryset=Session.objects.none(), empty_label="Pasirinkite sesiją")
    registration_date = forms.DateField(widget=SimpleDateWidget(), required=False)

    class Meta:
        model = Enrollment
        fields = ['child', 'session', 'registration_date']

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        club_id = kwargs.pop('club_id', None)
        super().__init__(*args, **kwargs)
        if parent:
            self.fields['child'].queryset = Child.objects.filter(parent=parent)
        if club_id:
            self.fields['session'].queryset = Session.objects.filter(club_id=club_id)

    def clean(self):
        cleaned_data = super().clean()
        child = cleaned_data.get('child')
        session = cleaned_data.get('session')
        if Enrollment.objects.filter(child=child, session=session).exists():
            raise forms.ValidationError("Šis vaikas jau užregistruotas į šią sesiją.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.registration_date = self.cleaned_data['registration_date']
        if commit:
            instance.save()
        return instance


class ContactForm(forms.Form):
    first_name = forms.CharField(label='Vardas', max_length=100)
    last_name = forms.CharField(label='Pavardė', max_length=100)
    email = forms.EmailField(label='El. paštas')
    message = forms.CharField(label='Žinutė', widget=forms.Textarea)
