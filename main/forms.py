from django import forms
import random
ALBUMS = ["Diamonds", "Scorpion", "beerbongs & bentleys", "ASTROWORLD", "Star Wars Revenge of the Sith", "Curtain Call"]
class URLForm(forms.Form):
    id = forms.CharField(max_length=100, label='',widget=forms.TextInput(attrs={'value': '6zhlos3HFJrWni7rjqxacg'}))

class PlaylistForm(forms.Form):
  id = forms.CharField(max_length=100, label='',widget=forms.TextInput(attrs={
    'value': random.choice(ALBUMS)
    }))