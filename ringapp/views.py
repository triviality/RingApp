from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.generic import DetailView, ListView, TemplateView, FormView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.template import RequestContext, loader
from ringapp.models import Ring, Property, Logic, RingProperty, Invariance
from ringapp.models import CommProperty, CommLogic, CommRingProperty, CommInvariance
from ringapp.models import Publication, Theorem, Suggestion, Keyword
from ringapp.forms import SearchForm, CommSearchForm, ContribSelector, RingSelector, KeywordSearchForm
import re
import random
import logging
vlogger = logging.getLogger('ringapp.vlogger')

from AdminUtils import *

class SearchPage(TemplateView):
    @property
    def template_name(self):
        if 'has' in self.request.GET or 'lacks' in self.request.GET:
            return 'ringapp/results.html'
        else:
            return 'ringapp/search.html'
            
    def get_context_data(self, **kwargs):
        context = super(SearchPage, self).get_context_data(**kwargs)
        if 'has' not in self.request.GET and 'lacks' not in self.request.GET:
            form = SearchForm()
            context['form'] = form
            return context
        else:
            has = lacks = tuple()
            if 'has' in self.request.GET:
                has = [int(thing) for thing in self.request.GET.getlist('has')]
            if 'lacks' in self.request.GET:
                lacks = [int(thing) for thing in self.request.GET.getlist('lacks')]

            has_names = [Property.objects.get(pk=x).name for x in has]
            lacks_names = [Property.objects.get(pk=x).name for x in lacks]
            has_string = ' and '.join(has_names)
            lacks_string = ' or '.join(lacks_names)

            main_results = find_rings('n', has=has, lacks=lacks)
            weak_results = find_rings('w', has=has, lacks=lacks)
            weak_results = set(weak_results) - set(main_results)
            
            mirror_results = mirror_search('n', has=has, lacks=lacks)
            m_weak_results = mirror_search('w', has=has, lacks=lacks)
            m_weak_results = set(m_weak_results) - set(mirror_results)      

            context.update({
               'has': has,
               'lacks': lacks,
               'main_results': main_results,
               'mirror_results': mirror_results,
               'weak_results': weak_results,
               'm_weak_results': m_weak_results,
               'has_string': has_string,
               'lacks_string': lacks_string,
               })
            return context
        

# TODO: clean this view out if new views work fine
def searchpage(request):
    if "scope" in request.GET:  # If the form has been submitted...
        form = SearchForm(request.GET)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            template = loader.get_template('ringapp/results.html')
            datadict = form.cleaned_data
            context = RequestContext(request, {'datadict': datadict})
            return HttpResponse(template.render(context))
    else:
        form = SearchForm()  # An unbound form

    return render(request, 'ringapp/search.html', {
        'form':  form,
    })   


class CommSearchPage(TemplateView):
    @property
    def template_name(self):
        if 'has' in self.request.GET or 'lacks' in self.request.GET:
            return 'ringapp/commresults.html'
        else:
            return 'ringapp/commsearch.html'
            
    def get_context_data(self, **kwargs):
        context = super(CommSearchPage, self).get_context_data(**kwargs)
        if 'has' not in self.request.GET and 'lacks' not in self.request.GET:
            form = CommSearchForm()
            context['form'] = form
            return context
        else:
            has = lacks = tuple()
            if 'has' in self.request.GET:
                has = [int(thing) for thing in self.request.GET.getlist('has')]
            if 'lacks' in self.request.GET:
                lacks = [int(thing) for thing in self.request.GET.getlist('lacks')]
            has_names = [CommProperty.objects.get(pk=x).name for x in has]
            lacks_names = [CommProperty.objects.get(pk=x).name for x in lacks] 
            has_string = ' and '.join(has_names)
            lacks_string = ' or '.join(lacks_names)
    
            main_results = find_rings('n', has=has, lacks=lacks, comm=True)
            weak_results = find_rings('w', has=has, lacks=lacks, comm=True)
            weak_results = set(weak_results) - set(main_results)

            context.update({'has': has,
                            'lacks': lacks,
                            'main_results': main_results,
                            'weak_results': weak_results,
                            'has_string': has_string,
                            'lacks_string': lacks_string,
                            })
            return context

class KeywordSearchPage(TemplateView):
    @property
    def template_name(self):
        if 'kwd' in self.request.GET:
            return 'ringapp/keywordresults.html'
        else:
            return 'ringapp/keywordsearch.html'
            
    def get_context_data(self, **kwargs):
        context = super(KeywordSearchPage, self).get_context_data(**kwargs)
        if 'kwd' not in self.request.GET:
            form = KeywordSearchForm()
            context['form'] = form
            return context
        else:
            kids = [int(thing) for thing in self.request.GET.getlist('kwd')]
            kwds = [Keyword.objects.get(pk=x) for x in kids]
            results = Ring.objects.all()
            for kwd in kwds:
                results = [ring for ring in results if kwd in ring.keywords.all()]

            context.update({'kwds': kwds, 'results': results})
            return context

# TODO: clean this view out if new views work fine
def commsearchpage(request):
    if "scope" in request.GET:  # If the form has been submitted...
        form = CommSearchForm(request.GET)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            template = loader.get_template('ringapp/commresults.html')
            datadict = form.cleaned_data
            context = RequestContext(request, {'datadict': datadict})
            return HttpResponse(template.render(context))
    else:
        form = CommSearchForm()  # An unbound form

    return render(request, 'ringapp/commsearch.html', {
        'form':  form,
    })

# TODO: clean this view out if new views work fine
def keywordsearchpage(request):
    if "kwd" in request.GET:  # If the form has been submitted...
        form = KeywordSearchForm(request.GET)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            template = loader.get_template('ringapp/keywordresults.html')
            datadict = form.cleaned_data
            context = RequestContext(request, {'datadict': datadict})
            return HttpResponse(template.render(context))
    else:
        form = KeywordSearchForm()  # An unbound form

    return render(request, 'ringapp/keywordsearch.html', {
        'form':  form,
    })


# TODO: clean this view out if new views work fine
def results(request):
    template = loader.get_template('ringapp/results.html')
    
    scope = request.GET['scope']
    has = lacks = tuple()
    if 'has' in request.GET.keys():
        has = [int(thing) for thing in request.GET.getlist('has')]
    if 'lacks' in request.GET.keys():
        lacks = [int(thing) for thing in request.GET.getlist('lacks')]

    has_names = [Property.objects.get(pk=x).name for x in has]
    lacks_names = [Property.objects.get(pk=x).name for x in lacks]
    has_string = ' and '.join(has_names)
    lacks_string = ' or '.join(lacks_names)

    main_results = find_rings(scope, has=has, lacks=lacks)
    mirror_results = mirror_search(scope, has=has, lacks=lacks)
    
    context = RequestContext(request, {
                                       'has': has,
                                       'lacks': lacks,
                                       'scope': scope,
                                       'main_results': main_results,
                                       'mirror_results': mirror_results,
                                       'has_string': has_string,
                                       'lacks_string': lacks_string,
                                       })
    return HttpResponse(template.render(context))

# TODO: clean this view out if new views work fine
def commresults(request):
    template = loader.get_template('ringapp/commresults.html')
    scope = request.GET['scope']
    has = lacks = tuple()
    if 'has' in request.GET.keys():
        has = [int(thing) for thing in request.GET.getlist('has')]
    if 'lacks' in request.GET.keys():
        lacks = [int(thing) for thing in request.GET.getlist('lacks')]
    has_names = [CommProperty.objects.get(pk=x).name for x in has]
    lacks_names = [CommProperty.objects.get(pk=x).name for x in lacks] 
    has_string = ' and '.join(has_names)
    lacks_string = ' or '.join(lacks_names)
    
    main_results = find_rings(scope, has=has, lacks=lacks, comm=True)
    
    context = RequestContext(request, {'has': has,
                                       'lacks': lacks,
                                       'scope': scope,
                                       'main_results': main_results,
                                       'has_string': has_string,
                                       'lacks_string': lacks_string,
                                       })
    return HttpResponse(template.render(context))

# TODO: clean this view out if new views work fine
def keywordresults(request):
    template = loader.get_template('ringapp/keywordresults.html')
    kids = []
    if 'kwd' in request.GET.keys():
        kids = [int(thing) for thing in request.GET.getlist('kwd')]
    kwds = [Keyword.objects.get(pk=x) for x in kids]
    results = Ring.objects.all()
    if not kwds:
        results = []
    else:
        for kwd in kwds:
            results = [ring for ring in results if kwd in ring.keywords.all()]

    context = RequestContext(request, {
                                       'kwds': kwds,
                                       'results': results,
                                       })
    return HttpResponse(template.render(context))


class RingList(ListView):
    model = Ring
    template_name = 'ringapp/ring_list.html'

    def get_queryset(self):
        queryset = list(Ring.objects.annotate(num_known=Count('ringproperty')))
        total = float(Property.objects.count())
        for item in queryset:
            item.num_known = round(item.num_known / total, 2)
        return queryset


class CommRingList(ListView):
    model = Ring
    template_name = 'ringapp/commring_list.html'

    def get_queryset(self):
        queryset = Ring.objects.filter(ringproperty__property=Property.objects.get(pk=1),
                                   ringproperty__has_property=1).annotate(num_known=Count('commringproperty'))
        total = float(CommProperty.objects.count())
        for item in queryset:
            item.num_known = round(item.num_known / total, 2)
        return queryset


class PropertyList(ListView):
    model = Property
    
    def get_queryset(self):
        return Property.objects.order_by('name')


class CommPropertyList(ListView):
    model = CommProperty

    def get_queryset(self):
        return CommProperty.objects.order_by('name')


class LogicList(ListView):
    model = Logic

    def get_queryset(self):
        Logic.objects.filter(option='on')


class CommLogicList(ListView):
    model = CommLogic

    def get_queryset(self):
        CommLogic.objects.filter(option='on')


def viewring(request, ring_id):
    r = Ring.objects.get(ring_id=ring_id)
    has_props = []
    lacks_props = []
    other_props = []
    for p in Property.objects.all():
        if r.ringproperty_set.filter(property=p, has_property=1):
            has_props.append((p.name.lower(), p))
        elif r.ringproperty_set.filter(property=p, has_property=0):
            lacks_props.append((p.name.lower(), p))
        else:
            other_props.append((p.name.lower(), p))
    has_props.sort()
    lacks_props.sort()
    other_props.sort()

    if has_props:
        has_props = zip(*has_props)[1]
    if lacks_props:
        lacks_props = zip(*lacks_props)[1]
    if other_props:
        other_props = zip(*other_props)[1]
    ref_list = ['%s, %s, %s, (%d). %s' % (x.publication.authors,
                                          x.publication.title,
                                          x.publication.details,
                                          x.publication.pub_date.year,
                                          x.location) for x in r.reference.all()]
    tags = r.keywords.all()
    context = RequestContext(request, {
        'r': r,
        'has_props': has_props,
        'lacks_props': lacks_props,
        'other_props': other_props,
        'ref_list': ref_list,
        'tags': tags,
    })
    template = loader.get_template('ringapp/viewring.html')
    return HttpResponse(template.render(context))


def viewcommring(request, ring_id):
    r = Ring.objects.get(ring_id=ring_id)
    has_props = []
    lacks_props = []
    other_props = []
    for p in CommProperty.objects.all():
        if r.commringproperty_set.filter(property=p, has_property=1):
            has_props.append((p.name.lower(), p))
        elif r.commringproperty_set.filter(property=p, has_property=0):
            lacks_props.append((p.name.lower(), p))
        else:
            other_props.append((p.name.lower(), p))
    has_props.sort()
    lacks_props.sort()
    other_props.sort()
    if has_props:
        has_props = zip(*has_props)[1]
    if lacks_props:
        lacks_props = zip(*lacks_props)[1]
    if other_props:
        other_props = zip(*other_props)[1]
    ref_list = ['%s, %s, %s, (%d). %s' % (x.publication.authors,
                                          x.publication.title,
                                          x.publication.details,
                                          x.publication.pub_date.year,
                                          x.location) for x in r.reference.all()]
    tags = r.keywords.all()
    context = RequestContext(request, {
        'r': r,
        'has_props': has_props,
        'lacks_props': lacks_props,
        'other_props': other_props,
        'ref_list': ref_list,
        'tags': tags,
    })
    template = loader.get_template('ringapp/viewcommring.html')
    return HttpResponse(template.render(context))
    

class PropertyView(DetailView):
    model = Property
    template_name = 'ringapp/property_detail.html'

    def get_context_data(self, **kwargs):
        context = super(PropertyView, self).get_context_data(**kwargs)
        hasnum = self.object.ringproperty_set.filter(has_property=1).count()
        lacksnum = self.object.ringproperty_set.filter(has_property=0).count()
        metaproperties = Invariance.objects.filter(property=self.object)
        has_mp = [x.metaproperty for x in metaproperties.filter(has_metaproperty=True)]
        lacks_mp = [x.metaproperty for x in metaproperties.filter(has_metaproperty=False)]

        context.update({
            'hasnum': hasnum,
            'lacksnum': lacksnum,
            'metaproperties': metaproperties,
            'has_mp': has_mp,
            'lacks_mp': lacks_mp,
        })

        return context    


class CommPropertyView(DetailView):
    model = CommProperty
    template_name = 'ringapp/commproperty_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CommPropertyView, self).get_context_data(**kwargs)

        hasnum = self.object.commringproperty_set.filter(has_property=1).count()
        lacksnum = self.object.commringproperty_set.filter(has_property=0).count()
        metaproperties = CommInvariance.objects.filter(property=self.object)
        has_mp = [x.metaproperty for x in metaproperties.filter(has_metaproperty=True)]
        lacks_mp = [x.metaproperty for x in metaproperties.filter(has_metaproperty=False)]

        context.update({
            'hasnum': hasnum,
            'lacksnum': lacksnum,
            'metaproperties': metaproperties,
            'has_mp': has_mp,
            'lacks_mp': lacks_mp,
        })
        return context


class SuggestionView(SuccessMessageMixin, CreateView):
    model=Suggestion
    template_name = 'ringapp/contribute.html'
    success_url = '/contribute/'
    fields = ['object_type', 'name', 'description']
    success_message = "Thanks... we'll look into that %(object_display)s suggestion!"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(SuggestionView, self).form_valid(form)    

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            object_display=self.object.get_object_type_display(),
        )

    def get_context_data(self, **kwargs):
        context = super(SuggestionView, self).get_context_data(**kwargs)
        with open('ringapp/generated/ring_sugg.txt', 'r') as f:
            ring_sugg = random.choice(f.readlines())
        with open('ringapp/generated/cring_sugg.txt', 'r') as f:
            cring_sugg = random.choice(f.readlines())
        context['ring_sugg'] = ring_sugg
        context['cring_sugg'] = cring_sugg
        return context
        


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'ringapp/profile.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['suggestions'] = Suggestion.objects.filter(user=self.request.user)
        
        return context
        

def contribute(request):
    if request.method == 'POST':  # If the form has been submitted...
        chooser = ContribSelector(request.POST)  # A form bound to the POST data
        if chooser.is_valid():  # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            template = loader.get_template('ringapp/suggestions.html')
            # choice = chooser.cleaned_data['option']
            context = RequestContext(request, {})
            return HttpResponse(template.render(context))
    else:
        chooser = ContribSelector()  # An unbound form
        template = loader.get_template('ringapp/contribute.html')
        context = RequestContext(request, {'chooser': chooser})
        return HttpResponse(template.render(context))


def suggestions(request):
    template = loader.get_template('ringapp/suggestions.html')
    data = dict(item for item in request.GET.items())
    # cite_sugg = 
    with open('ringapp/generated/ring_sugg.txt', 'r') as f:
        ring_sugg = random.choice(f.readlines())
    with open('ringapp/generated/cring_sugg.txt', 'r') as f:
        cring_sugg = random.choice(f.readlines())
    # data['cite_sugg'] = cite_sugg
    data['ring_sugg'] = ring_sugg
    data['cring_sugg'] = cring_sugg
    context = RequestContext(request, data)
    return HttpResponse(template.render(context))


class TheoremDetail(DetailView):
    template_name = 'ringapp/theorem_detail.html'
    model = Theorem
    
    def get_context_data(self, **kwargs):
        context = super(TheoremDetail, self).get_context_data(**kwargs)
        ref_list = ['%s, %s, %s, (%d). %s' % (x.publication.authors,
                                              x.publication.title,
                                              x.publication.details,
                                              x.publication.pub_date.year,
                                              x.location) for x in self.object.reference.all()]
        context['ref_list'] = ref_list
        return context


def bibliography(request):
    template = loader.get_template('ringapp/bibliography.html')
    bib = ['%s, %s, %s, (%d).' % (x.authors,
                                  x.title,
                                  x.details,
                                  x.pub_date.year) for x in Publication.objects.exclude(id__in=[6, 10])]
    bib.sort()
    context = RequestContext(request, {'bibliography': bib})
    return HttpResponse(template.render(context))


def processor(request):
    if request.method == 'POST':  # If the form has been submitted...
        form = RingSelector(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # Process the data in form.cleaned_data
            ring_id = request.POST['ring']
            ring = Ring.objects.get(ring_id=ring_id)
            comm = Property.objects.get(name='commutative')
            rps = ring.ringproperty_set.filter(property=comm, has_property=1)
            if rps.exists():
                modes = [False, True]
            else:
                modes = [False]
            try:
                for mode in modes:
                    ctr = 0
                    check = True
                    while ctr < 15 and check is True:
                        check = new_single_logic_forward(ring, comm=mode)
                        ctr += 1
                        if check == -1:
                            raise Exception("SingleLogicForward conflict")
                    if ctr == 15:
                        vlogger.error('New single logic forward script ran too many times on ring_id=%s comm=%s.'
                                      % (str(ring.ring_id), str(mode)))
                    ctr = 0
                    check = True
                    while ctr < 15 and check is True:
                        check = new_single_logic_backward(ring, comm=mode)
                        ctr += 1
                        if check == -1:
                            raise Exception("SingleLogicBackward conflict")
                    if ctr == 15:
                        vlogger.error('New single logic backward script ran too many times on ring_id=%s comm=%s.'
                                      % (str(ring.ring_id), str(mode)))
                msg = "Processing of %s was successful" % str(ring)
            except Exception:
                msg = 'Exception occurred during processing. Alert an admin.'

            template = loader.get_template('admin/processor.html')
            context = RequestContext(request, {'form': form, 'msg': msg})
            return HttpResponse(template.render(context))
    else:
        form = RingSelector()  # An unbound form
    template = loader.get_template('admin/processor.html')
    context = RequestContext(request, {'form': form})
    return HttpResponse(template.render(context))
