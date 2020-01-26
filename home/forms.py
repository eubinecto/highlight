from django import forms


# This form is on its own
# Have to manually link to database
class VideoURLForm(forms.Form):
    url = forms.CharField(max_length=200, required=True)

