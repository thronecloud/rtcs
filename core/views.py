from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.views.generic.detail import DetailView

from .models import CabRequest


def index_view(request):
    return render(request, 'core/index.html')


class CreateCabRequest(CreateView):
    model = CabRequest
    fields = ['moment', 'gender', 'origin', 'destination']

    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        return super(CreateCabRequest, self).form_valid(form)

    def get_success_url(self):
        return reverse('user_profile')


class CabRequestDetail(DetailView):
    model = CabRequest

    def get_context_data(self, **kwargs):
        context = super(CabRequestDetail, self).get_context_data(**kwargs)
        context['matches'] = self.object.matches\
            .filter(route_overlap__gt=-1)\
            .order_by("-route_overlap").order_by("-affinity")
        return context


class CabRequestDelete(DeleteView):
    model = CabRequest

    def get_success_url(self):
        return reverse('user_profile')


def userdetail_view(request):
    user = request.user
    return render(request, 'core/userdetail.html', dict(user=user))
