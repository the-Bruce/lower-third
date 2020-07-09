from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils import timezone
from django.shortcuts import get_object_or_404
import datetime

from django.views.generic import TemplateView, View
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Session, new_key, Scene


# Create your views here.
class DisplayView(TemplateView):
    template_name = "LowerThird/display.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Session.objects.filter(date__lte=timezone.now() - datetime.timedelta(days=5)).delete()
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
        return context


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
