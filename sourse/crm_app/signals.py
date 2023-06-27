# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from .models import ModelChangeLog
#
#
# @receiver(post_save, dispatch_uid='log_model_change')
# def log_model_change(sender, instance, created, **kwargs):
#     if sender != ModelChangeLog:
#         if created:
#             change_type = 'Created'
#         else:
#             change_type = 'Updated'
#
#         log_entry = ModelChangeLog(model_name=sender.__name__, change_type=change_type)
#         log_entry.save()
#
#
# @receiver(post_delete, dispatch_uid='log_model_delete')
# def log_model_delete(sender, instance, **kwargs):
#     if sender != ModelChangeLog:
#         log_entry = ModelChangeLog(model_name=sender.__name__, change_type='Deleted')
#         log_entry.save()
