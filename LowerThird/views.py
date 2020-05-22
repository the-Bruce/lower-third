from django.utils import timezone
import datetime

from django.views.generic import TemplateView, View
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Session


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
                    "l1": "",
                    "l2": "",
                }
            else:
                ret = {
                    "state": session.state,
                    "l1": session.scene.line1,
                    "l2": session.scene.line2,
                }
        return JsonResponse(ret)


class Control(TemplateView):
    template_name = "LowerThird/control.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Session.objects.filter(date__lte=timezone.now() - datetime.timedelta(days=5)).delete()
        session = Session.objects.get_or_404(session=self.request.session['session'])
        context['ses'] = session
        return context
