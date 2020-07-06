import random
from django.db.models import F, Func
from django.db.models.functions import Greatest
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import View, TemplateView

# Create your views here.

from Count.models import DayCount, LogItem


class MainView(TemplateView):
    template_name = "Count/main.html"

    @method_decorator(ensure_csrf_cookie)
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctxt = super().get_context_data(**kwargs)
        if 'id' not in self.request.session:
            self.request.session['id'] = random.randrange(1, 999999999)
        ctxt['device_id']=self.request.session['id']
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

            next = max(dc.current + delta, 0)
            total = dc.total + max(delta, 0)
            peak = max(dc.current + delta, dc.peak)
            dc.peak = Greatest(F('current') + delta, F('peak'))
            dc.total = F('total') + Greatest(delta, 0)
            dc.current = Greatest(F('current') + delta, 0)
            dc.save()

            ret = {
                "count": next,
                "total": total,
                "peak": peak,
            }
            return JsonResponse(ret)
