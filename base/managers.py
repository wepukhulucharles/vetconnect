"""
Custom managers and querysets for optimized database queries
"""
from django.db import models
from django.db.models import Prefetch


class OptimizedConsultationQuerySet(models.QuerySet):
    """QuerySet with common optimizations for Consultation model"""
    
    def with_related(self):
        """Optimize queries with related objects"""
        return self.select_related(
            'vet',
            'client',
            'vet__user'
        ).prefetch_related('secondary_consultants')
    
    def pending(self):
        """Filter for pending consultations"""
        return self.filter(status='PENDING')
    
    def accepted(self):
        """Filter for accepted consultations"""
        return self.filter(status='ACCEPTED')
    
    def completed(self):
        """Filter for completed consultations"""
        return self.filter(status='COMPLETED')


class OptimizedConsultationManager(models.Manager):
    """Manager for Consultation model"""
    
    def get_queryset(self):
        return OptimizedConsultationQuerySet(self.model, using=self._db)
    
    def with_related(self):
        return self.get_queryset().with_related()
    
    def pending(self):
        return self.get_queryset().pending()
    
    def accepted(self):
        return self.get_queryset().accepted()
    
    def completed(self):
        return self.get_queryset().completed()


class OptimizedAppointmentQuerySet(models.QuerySet):
    """QuerySet with common optimizations for Appointment model"""
    
    def with_related(self):
        """Optimize queries with related objects"""
        return self.select_related('vet', 'client')
    
    def pending(self):
        """Filter for pending appointments"""
        return self.filter(status='PENDING')
    
    def upcoming(self):
        """Filter for upcoming appointments"""
        from django.utils import timezone
        return self.filter(
            scheduled_date__gte=timezone.now().date()
        ).order_by('scheduled_date', 'scheduled_time_from')


class OptimizedAppointmentManager(models.Manager):
    """Manager for Appointment model"""
    
    def get_queryset(self):
        return OptimizedAppointmentQuerySet(self.model, using=self._db)
    
    def with_related(self):
        return self.get_queryset().with_related()
    
    def pending(self):
        return self.get_queryset().pending()
    
    def upcoming(self):
        return self.get_queryset().upcoming()


class OptimizedNotificationQuerySet(models.QuerySet):
    """QuerySet with common optimizations for Notification model"""
    
    def unread(self):
        """Filter for unread notifications"""
        return self.filter(is_read=False)
    
    def for_user(self, user):
        """Filter notifications for a specific user"""
        return self.filter(user=user)


class OptimizedNotificationManager(models.Manager):
    """Manager for Notification model"""
    
    def get_queryset(self):
        return OptimizedNotificationQuerySet(self.model, using=self._db)
    
    def unread(self):
        return self.get_queryset().unread()
    
    def for_user(self, user):
        return self.get_queryset().for_user(user)
    
    def unread_for_user(self, user):
        """Get unread notifications for a user"""
        return self.get_queryset().for_user(user).unread()
