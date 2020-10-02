from django import forms
from string import Template
from django.utils.safestring import mark_safe
from .models import Profile, User

# class ImageWidget(forms.widgets.Widget):
#     def render(self, name, value, attrs=None, **kwargs):
#         html= Template("""<img src="$link"/>""")
#         return mark_safe(html.substitute(link=value))

class ImageForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput(attrs={'class':'fileinput fileinput-new text-center','id':'imageField'}))
    
    class Meta:
        model = Profile
        fields = ['image']
        
class ProfileForm(forms.ModelForm):
    summary = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}))
    interest = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}))
    goals = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}))

    class Meta:
        model = Profile
        fields = ['summary','interest','goals']

class UserForm(forms.ModelForm):

    YEARS = []
    x = 0
    for x in range(1910, 2003):
        YEARS.append(str(x))

    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    birthday = forms.DateField(widget=forms.SelectDateWidget(attrs={'class':'form-control','style': 'width: 33%; display: inline-block;'}, years=YEARS))
    gender = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'} ))
    city = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))


    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'birthday', 'gender', 'city' ]