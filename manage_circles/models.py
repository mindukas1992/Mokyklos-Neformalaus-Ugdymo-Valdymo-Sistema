from django.conf import settings
from django.db import models
from tinymce.models import HTMLField


class Parent(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parent')
    first_name = models.CharField('Vardas', max_length=50, null=False)
    last_name = models.CharField('Pavardė', max_length=50, null=False)
    email = models.CharField('El_paštas', max_length=50, null=False)
    phone_number = models.CharField('Telefono_numeris', max_length=50, null=False)
    address = models.CharField('Adresas', max_length=200, null=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Child(models.Model):
    first_name = models.CharField('Vaiko_vardas', max_length=50, null=False)
    last_name = models.CharField('Vaiko_pavardė', max_length=50, null=False)
    child_age = models.IntegerField('Vaiko_metai', null=False)
    school = models.CharField('Mokykla', max_length=100, null=False)
    classroom = models.CharField('Klasė/grupė', max_length=50, null=False)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='children')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Club(models.Model):
    name = models.CharField(max_length=100, verbose_name="Būrelio pavadinimas")
    cover = models.ImageField('Viršelis', upload_to='images', null=True)
    description = HTMLField()
    activity_type = models.CharField(max_length=50, choices=(
        ('artistic', 'Meninė'),
        ('scientific', 'Mokslinė'),
        ('sports', 'Sportinė'),
    ), verbose_name="Veiklos tipas")

    def __str__(self):
        return f'{self.name}'


class Session(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='sessions')
    day_of_week = models.CharField('Savaitės diena', max_length=20, choices=[
        ('Pirmadienis', 'Pirmadienis'),
        ('Antradienis', 'Antradienis'),
        ('Trečiadienis', 'Trečiadienis'),
        ('Ketvirtadienis', 'Ketvirtadienis'),
        ('Penktadienis', 'Penktadienis'),
        ('Šeštadienis', 'Šeštadienis'),
        ('Sekmadienis', 'Sekmadienis'),
    ])
    start_time = models.TimeField('Pradžios laikas')
    end_time = models.TimeField('Pabaigos laikas')
    group = models.CharField(max_length=100, choices=[
        ('Priešmokyklinukai', 'Priešmokyklinukai'),
        ('Pirmokai – septintokai', 'Pirmokai – septintokai'),
        ('Priešmokyklinukai - pirmokai', 'Priešmokyklinukai - pirmokai'),
        ('Antrokai – septintokai', 'Antrokai – septintokai'),
        ('Pirmokai – šeštokai', 'Pirmokai – šeštokai'),
        ('Antrokai – ketvirtokai', 'Antrokai – ketvirtokai'),
        ('Pirmokai – ketvirtokai', 'Pirmokai – ketvirtokai'),
        ('Penktokai – septintokai', 'Penktokai – septintokai'),
        ('Penktokai – aštuntokai', 'Penktokai – aštuntokai'),
        ('Priešmokyklinukai - aštuntokai', 'Priešmokyklinukai - aštuntokai'),
        ('Naujokai ir oranžiniai diržai', 'Naujokai ir oranžiniai diržai'),
        ('Pažengę (nuo mėlynų juostelių) ir vyresni naujokai (9+ metų)',
         'Pažengę (nuo mėlynų juostelių) ir vyresni naujokai (9+ metų)'),
        ('Trijų – keturių metų', 'Trijų – keturių metų'),
        ('Penkių – šešių metų', 'Penkių – šešių metų'),
        ('Septynių – dešimties metų', 'Septynių – dešimties metų'),
        ('Priešmokyklinukai (1 grupė)', 'Priešmokyklinukai (1 grupė)'),
        ('Priešmokyklinukai (2 grupė)', 'Priešmokyklinukai (2 grupė)'),
        ('Visi nuo dešimties metų', 'Visi nuo dešimties metų'),
    ])

    def __str__(self):
        return f"{self.club.name} - {self.day_of_week} {self.start_time}-{self.end_time} ({self.group})"


class Enrollment(models.Model):
    child = models.ForeignKey('Child', on_delete=models.CASCADE, related_name='enrollments')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='enrollments')
    registration_date = models.DateField(null=True)

    def __str__(self):
        return f"{self.child} - {self.session} - {self.registration_date}"
