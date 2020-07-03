from django.db.models import F, Func
from django.db.models.functions import Greatest
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import View

# Create your views here.

from Count.models import DayCount


class MainView(View):
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return render(request, 'Count/main.html')


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
        next = max(dc.current + delta, 0)
        total = dc.total + max(delta, 0)
        peak = max(dc.current+delta, dc.peak)
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
