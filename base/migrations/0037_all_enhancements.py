# Generated migration for all enhancements

from django.db import migrations, models
import django.db.models.deletion
import base.validators


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0036_remove_vet_associated_institutions_portfolio_and_more'),  # Adjust this based on your last migration
    ]

    operations = [
        # Add new fields to existing models
        migrations.AddField(
            model_name='referralcolleaguerequest',
            name='expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='consultation',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='consultation',
            name='status',
            field=models.CharField(
                choices=[
                    ('PENDING', 'PENDING'),
                    ('ACCEPTED', 'ACCEPTED'),
                    ('IN_PROGRESS', 'IN_PROGRESS'),
                    ('COMPLETED', 'COMPLETED'),
                    ('CANCELLED', 'CANCELLED'),
                    ('REJECTED', 'REJECTED'),
                ],
                db_index=True,
                default='PENDING',
                max_length=15
            ),
        ),
        migrations.AddField(
            model_name='consultationfee',
            name='payment_status',
            field=models.CharField(
                choices=[
                    ('PENDING', 'Pending'),
                    ('PAID', 'Paid'),
                    ('REFUNDED', 'Refunded'),
                    ('CANCELLED', 'Cancelled'),
                ],
                default='PENDING',
                max_length=15
            ),
        ),
        migrations.AddField(
            model_name='consultationfee',
            name='refunded_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='consultationfee',
            name='cancellation_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='consultationsatisfactioncomment',
            name='review_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='consultationsatisfactioncomment',
            name='vet_response',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='consultationsatisfactioncomment',
            name='vet_response_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='consultationsatisfactioncomment',
            name='is_flagged',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='consultationsatisfactioncomment',
            name='flag_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='buffer_time_minutes',
            field=models.IntegerField(default=30),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='status',
            field=models.CharField(
                choices=[
                    ('PENDING', 'PENDING'),
                    ('ACCEPTED', 'ACCEPTED'),
                    ('REJECTED', 'REJECTED'),
                    ('COMPLETED', 'COMPLETED'),
                    ('CANCELLED', 'CANCELLED'),
                ],
                db_index=True,
                default='PENDING',
                max_length=15
            ),
        ),
        migrations.AddField(
            model_name='notification',
            name='category',
            field=models.CharField(
                choices=[
                    ('COLLEAGUE', 'Colleague Request'),
                    ('APPOINTMENT', 'Appointment'),
                    ('CONSULTATION', 'Consultation'),
                    ('RATING', 'Rating/Review'),
                    ('SYSTEM', 'System'),
                ],
                default='SYSTEM',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='notification',
            name='related_object_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='related_object_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        # Add indexes
        migrations.AddIndex(
            model_name='vet',
            index=models.Index(fields=['licence_expired', '-client_rating'], name='vet_active_rating_idx'),
        ),
        migrations.AddIndex(
            model_name='consultation',
            index=models.Index(fields=['status', '-created'], name='consult_status_created_idx'),
        ),
        migrations.AddIndex(
            model_name='appointment',
            index=models.Index(fields=['status', 'scheduled_date'], name='appt_status_scheduled_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['user', 'is_read', '-timestamp'], name='notif_user_read_ts_idx'),
        ),
        # Add constraints
        migrations.AddConstraint(
            model_name='referralcolleaguerequest',
            constraint=models.UniqueConstraint(
                condition=models.Q(('status', 'PENDING')),
                fields=['requesting_vet', 'colleague_requested'],
                name='unique_pending_colleague_request'
            ),
        ),
        # Create new models
        migrations.CreateModel(
            name='VetAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.IntegerField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')])),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('is_available', models.BooleanField(default=True)),
                ('break_start', models.TimeField(blank=True, null=True)),
                ('break_end', models.TimeField(blank=True, null=True)),
                ('vet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availability_slots', to='base.vet')),
            ],
            options={
                'ordering': ['day_of_week', 'start_time'],
                'unique_together': {('vet', 'day_of_week')},
            },
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete'), ('STATUS_CHANGE', 'Status Change')], max_length=20)),
                ('model_name', models.CharField(db_index=True, max_length=50)),
                ('object_id', models.IntegerField()),
                ('old_values', models.JSONField(blank=True, null=True)),
                ('new_values', models.JSONField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.User')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['model_name', 'object_id'], name='action_log_model_obj_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['user', 'timestamp'], name='action_log_user_ts_idx'),
        ),
    ]
