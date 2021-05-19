from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.syndication.views import Feed
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404
import datetime

from django.views.generic import TemplateView, View, FormView
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseRedirect

from . import forms
from .models import Session, new_key, Scene


# Create your views here.
class DisplayView(TemplateView):
    template_name = "LowerThird/display.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Session.objects.filter(date__lte=timezone.now() - datetime.timedelta(days=1)).delete()
        if 'session' in self.request.session:
            print('1:', self.request.session['session'])
            session, suc = Session.objects.get_or_create(session=self.request.session['session'])
        else:
            session = Session.objects.create()
            self.request.session['session'] = session.session
            print('2:', self.request.session['session'])

        context['ses'] = session
        return context


class ControlView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "LowerThird/control.html"
    permission_required = "LowerThird.view_session"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Session.objects.filter(date__lte=timezone.now() - datetime.timedelta(days=5)).delete()
        session = get_object_or_404(Session, session=self.kwargs['session'])
        session.key = new_key()
        session.save()
        context['ses'] = session
        self.session = session
        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if self.session.program is None:
            return HttpResponseRedirect(
                reverse('lower_third:program_select', kwargs={'session': self.kwargs['session']}))
        else:
            return response


class SessionView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    template_name = "LowerThird/form.html"
    permission_required = "LowerThird.view_session"
    form_class = forms.SessionSelectForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Select Session"
        return context

    def form_valid(self, form):
        return HttpResponseRedirect(form.cleaned_data['session'].get_absolute_url())


class ProgramSelectView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    template_name = "LowerThird/form.html"
    permission_required = "LowerThird.view_session"
    form_class = forms.ProgramSelectForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = get_object_or_404(Session, session=self.kwargs['session'])
        context['ses'] = session
        self.session = session
        context['title'] = "Update Program"
        return context

    def form_valid(self, form):
        self.get_context_data()
        self.session.set_program(form.cleaned_data['program'])
        return HttpResponseRedirect(reverse('lower_third:control', kwargs={'session': self.kwargs['session']}))


class CurrentState(View):
    def get(self, request):
        if 'session' not in self.request.GET:
            return HttpResponseBadRequest(request, reason="Missing required key: session")
        else:
            try:
                session = Session.objects.get(session=self.request.GET['session'])
            except (Session.DoesNotExist, Session.MultipleObjectsReturned):
                return HttpResponseBadRequest(request, reason="Invalid key: session")

            if session.scene is None:
                ret = {
                    "state": session.state,
                    "scene": session.scene_id,
                    "l1": "",
                    "l2": "",
                }
            else:
                ret = {
                    "state": session.state,
                    "scene": session.scene_id,
                    "l1": session.scene.line1,
                    "l2": session.scene.line2,
                }
        return JsonResponse(ret)


class CurrentStateRSS(Feed):
    title = "Current State"
    link = reverse_lazy("lower_third:session_select")

    def get_object(self, request, session):
        a,n= Session.objects.get_or_create(session=session)
        return a

    def description(self, obj: Session):
        return "The current state of session"

    def items(self, obj: Session):
        if obj.scene is None:
            return [("line1", "Initialising"), ("line2",obj.session)]
        return [("line1", obj.scene.line1), ("line2", obj.scene.line2)]

    def item_title(self, item):
        return item[0]

    def item_description(self, item):
        return item[1]

    def item_link(self, item):
        return reverse("lower_third:session_select")


class CurrentStateListRSS(Feed):
    title = "Current State"
    link = reverse_lazy("lower_third:session_select")

    def get_object(self, request, session):
        a,n= Session.objects.get_or_create(session=session)
        return a

    def description(self, obj: Session):
        return "The current state of session"

    def items(self, obj: Session):
        if obj.scene is None:
            return [("Initialising", obj.session)]
        return [(a.line1, a.line2) for a in obj.program.scenes.order_by("order").all()]

    def item_title(self, item):
        return item[0]

    def item_description(self, item):
        return item[1]

    def item_link(self, item):
        return reverse("lower_third:session_select")


class UpdateState(View):
    def post(self, request):
        print(self.request.POST)
        if 'session' not in self.request.POST:
            return HttpResponseBadRequest(request, reason="Missing required key: session")
        elif 'key' not in self.request.POST:
            return HttpResponseBadRequest(request, reason="Missing required key: key")
        elif 'scene' not in self.request.POST:
            return HttpResponseBadRequest(request, reason="Missing required key: scene")
        elif 'state' not in self.request.POST:
            return HttpResponseBadRequest(request, reason="Missing required key: state")
        else:
            try:
                session = Session.objects.get(session=self.request.POST['session'])
            except (Session.DoesNotExist, Session.MultipleObjectsReturned):
                return HttpResponseBadRequest(request, reason="Invalid key: session")

            if session.key != self.request.POST['key']:
                return HttpResponseBadRequest(request, reason="Invalid key: key")

            if self.request.POST['state'] not in session.States():
                return HttpResponseBadRequest(request, reason="Invalid key: state")

            try:
                scene = Scene.objects.get(id=self.request.POST['scene'])
            except (Session.DoesNotExist, Session.MultipleObjectsReturned):
                return HttpResponseBadRequest(request, reason="Invalid key: scene")

            session.scene = scene
            session.state = self.request.POST['state']
            session.save()

            ret = {
                "state": session.state,
                "scene": session.scene_id,
                "l1": session.scene.line1,
                "l2": session.scene.line2,
            }
        return JsonResponse(ret)
