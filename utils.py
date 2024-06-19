from django.contrib.admin.models import ADDITION, LogEntry, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.db import models


def obj_delete(request, model, pk):
    """
    Функция для удаление объекта.
    - с записью в логи
    - с помощью Ajax
    - зарегистрированный пользователь
    """
    result = {'errors': True, 'mess': ''}
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            obj = model.objects.get(id=pk)
        except model.DoesNotExist:
            obj = None
            result['mess'] = 'Записи не существует'
        if obj:
            try:
                log = LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ContentType.objects.get_for_model(model).pk,
                    object_id=obj.id,
                    object_repr=str(obj),
                    action_flag=DELETION,
                    change_message='Объект был удален', 
                )
                obj.delete()
                log.save()
                result['errors'] = False
            except models.ProtectedError as err:
                result['mess'] = 'Не может быть удалено, потому что есть зависимости'
        
    return result


def redirect_next(request):
    """
    Редирект next с учетом существующих параметров в урл
    """
    nxt = request.GET.get("nxt", None)
    if nxt is None or nxt == 'None':
        return redirect(settings.LOGIN_REDIRECT_URL)
    elif not url_has_allowed_host_and_scheme(
            url=nxt,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure()):
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        return redirect(nxt)
    