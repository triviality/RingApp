from django import forms
from ringapp.models import Property, CommProperty, Ring, Keyword

scope_choices = [('n', 'Narrow'), ('w', 'Wide')]


class SearchForm(forms.Form):
    has = forms.ModelChoiceField(queryset=Property.objects.all().order_by('name'),
                                 widget=forms.SelectMultiple(attrs={'size':'15'}),
                                 empty_label=None)
    lacks = forms.ModelChoiceField(queryset=Property.objects.all().order_by('name'),
                                   widget=forms.SelectMultiple(attrs={'size':'15'}),
                                   empty_label=None)


class CommSearchForm(forms.Form):
    has = forms.ModelChoiceField(queryset=CommProperty.objects.all().order_by('name'),
                                 widget=forms.SelectMultiple(attrs={'size':'15'}),
                                 empty_label=None)
    lacks = forms.ModelChoiceField(queryset=CommProperty.objects.all().order_by('name'),
                                   widget=forms.SelectMultiple(attrs={'size':'15'}),
                                   empty_label=None)


class ContribSelector(forms.Form):
    option = forms.ChoiceField(choices=[('ring', 'I want to suggest a ring.'),
                                        ('theorem', 'I want to suggest a theorem.'),
                                        ('citation', 'I want to suggest a citation.'),
                                        ('randring', 'Give me an idea for a ring!'),
                                        ('randcite', 'Give me an idea for a citation!'),
                                        ('property', 'I want to suggest a property.')])


class RingSelector(forms.Form):
    ring = forms.ModelChoiceField(queryset=Ring.objects.all().order_by('name'))


class KeywordSearchForm(forms.Form):
    kwd = forms.ModelChoiceField(queryset=Keyword.objects.all().order_by('name'), 
                                 widget=forms.SelectMultiple(attrs={'size':'15'}),
                                 empty_label=None)
