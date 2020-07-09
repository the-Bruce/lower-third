import datetime
import random

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import F
from django.db.models.functions import Greatest
from django.http import HttpResponseBadRequest, JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import View, TemplateView

from Count.models import DayCount, LogItem, Graph


# Create your views here.


class MainView(TemplateView):
    template_name = "Count/main.html"

    @method_decorator(ensure_csrf_cookie)
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctxt = super().get_context_data(**kwargs)
        if 'id' not in self.request.session:
            self.request.session['id'] = random.randrange(1, 999999999)
        ctxt['device_id'] = self.request.session['id']
        return ctxt


class GraphView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "Count/graph.html"
    permission_required = "Count.view_graph"

    def get_context_data(self, **kwargs):
        ctxt = super().get_context_data(**kwargs)
        req_date = datetime.date(day=self.kwargs['day'], month=self.kwargs['month'], year=self.kwargs['year'])
        ctxt['date'] = req_date
        ctxt['prev'] = req_date - datetime.timedelta(days=1)
        ctxt['next'] = req_date + datetime.timedelta(days=1)

        if req_date < datetime.date.today():
            try:
                dc = DayCount.objects.get(date=req_date)
                g, n = Graph.objects.get_or_create(date=dc)
                ctxt['graph'] = g.graph_safe
            except (DayCount.MultipleObjectsReturned, DayCount.DoesNotExist):
                ctxt['graph'] = None
                ctxt['error'] = "No data available for the selected date"
                ctxt['error_level'] = "info"
        elif req_date == datetime.date.today():
            ctxt['graph'] = None
            ctxt['error'] = "Data still collecting. Please check back tomorrow"
            ctxt['error_level'] = "success"
        else:
            ctxt['graph'] = None
            ctxt['error'] = "No data available for the selected date"
            ctxt['error_level'] = "info"
        return ctxt


class CurrentState(View):
    def get(self, request):
        try:
            dc, new = DayCount.objects.get_or_create(date=timezone.now())
        except DayCount.MultipleObjectsReturned:
            return HttpResponseBadRequest(request, reason="Duplicate Days")

        ret = {
            "count": dc.current,
            "total": dc.total,
            "peak": dc.peak,
        }
        return JsonResponse(ret)


class UpdateState(View):
    def post(self, request):
        if 'device' not in self.request.POST:
            return HttpResponseBadRequest(request, reason="Missing required key: device")
        else:
            try:
                dc, new = DayCount.objects.get_or_create(date=timezone.now())
            except DayCount.MultipleObjectsReturned:
                return HttpResponseBadRequest(request, reason="Duplicate Days")

            try:
                delta = int(request.POST['change'])
                if abs(delta) > 100:
                    return HttpResponseBadRequest(request, reason="Invalid Change")
            except ValueError:
                return HttpResponseBadRequest(request, reason="Invalid Change")

            if request.user.is_authenticated:
                LogItem.objects.create(deviceID=self.request.POST['device'], userID=request.user, delta=delta)
            else:
                LogItem.objects.create(deviceID=self.request.POST['device'], delta=delta)

            next_ = max(dc.current + delta, 0)
            total = dc.total + max(delta, 0)
            peak = max(dc.current + delta, dc.peak)
            dc.peak = Greatest(F('current') + delta, F('peak'))
            dc.total = F('total') + Greatest(delta, 0)
            dc.current = Greatest(F('current') + delta, 0)
            dc.save()

            ret = {
                "count": next_,
                "total": total,
                "peak": peak,
            }
            return JsonResponse(ret)
