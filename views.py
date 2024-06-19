from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone

from vizit.models import Vizit


def vw_calendar(request):
    """
    Вывод календаря-расписания записи пациентов
    """
    times = []
    for hour in range(8, 20):
        for minute in range(0, 60, 30):
            times.append('{:02d}:{:02d}'.format(hour, minute))

    dates = [timezone.now().date() + timedelta(days=x) for x in range(3)]

    vizit = Vizit.objects.select_related('client', 'doctor', 'doctor__scheduletmpl')\
        .filter(vizited__date__gte=dates[0], vizited__date__lte=dates[-1]).exclude(status_id__in=[8, 9])
    doctor = get_user_model().objects.filter(position='doctor').exclude(is_block=True).select_related('scheduletmpl')
    post = request.GET.get('post', None)
    if post:
        doctor = doctor.filter(speciality=post)
    doctor_count = doctor.count()
    objs = [
        {'tt': 'date', 'data': [{'tt': n, 'colspan': doctor_count, 'today': True if n == datetime.today().date() else False} for n in dates]},
        {'tt': 'doctor', 'data': [[{'tt': u.get_full_name()} for u in doctor] for n in dates]},
    ]

    for t in times:
        tl = []
        for d in dates:
            dl = []
            for u in doctor:
                schedule_doctor = u.scheduletmpl
                work = False
                # 2024-04-10 10:30:00
                if schedule_doctor.start and schedule_doctor.end and schedule_doctor.start <= d <= schedule_doctor.end:
                    workday = getattr(schedule_doctor, d.strftime("%A").lower()).split()
                    if (workday):
                        time_up = datetime.strptime(workday[0].strip(), '%H:%M').time()
                        time_to = datetime.strptime(workday[-1].strip(), '%H:%M').time()
                        time_th = datetime.strptime(t, '%H:%M').time()
                        if time_up <= time_th <= time_to:
                            work = True
                try:
                    cell = vizit.get(vizited=datetime.strptime(f'{d} {t}', '%Y-%m-%d %H:%M'), doctor=u)
                    end = (cell.vizited + timedelta(minutes=cell.step)).strftime('%H:%M')
                except Vizit.DoesNotExist:
                    cell = end = None
                dl.append({'date': d, 'time': t, 'end': end, 'doctor': u, 'vizit': cell, 'work': work})
            tl.extend(dl)
        objs.append({'time': t, 'tt': 'vizit', 'data': tl})



@login_required
def vw_products(request):
    """
    Вывод и управление всего товара со склада в единой таблице
    """
    trade = Trade.objects.filter(product_id=OuterRef("id")).select_related('status')
    objs = Product.objects.filter(is_hide=False)\
        .select_related('ctg', 'ctg__parent', 'unit').prefetch_related('trade_set').order_by('ctg__tt', 'tt')\
        .annotate(
            buy_num=Sum('trade__num', filter=Q(trade__status__is_in=True), default=0),
            sell_num=Sum('trade__num', filter=Q(trade__status__is_in=False), default=0),
            buy_latest=Subquery(trade.filter(status__is_in=True).order_by("-created").values('cost')[:1]),
            sell_latest=Subquery(trade.filter(status__is_in=False).order_by("-created").values('cost')[:1]),
            buy_or=F('buy_latest') if F('buy_latest') else F('buy'),
            sell_or=F('sell_latest') if F('sell_latest') else F('sell'),  # TODO: if not work
            buy_total=Sum('trade__total', filter=Q(trade__status__is_in=True), default=0),
            sell_total=Sum('trade__total', filter=Q(trade__status__is_in=False), default=0),
            num_diff=F('buy_num') - F('sell_num'),
            minimum=F('num_diff') - F('min'),
    ).annotate(
            buy_itog=F('num_diff') * F('buy_or'),
            sell_itog=F('num_diff') * F('sell_or'),
    )

    report_end = '{0:,}'.format(objs.exclude(min=None).filter(minimum__lt=0).count()).replace(',', ' ')
