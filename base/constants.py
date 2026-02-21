# Central location for all choice constants

SPECIALIZATION_CHOICES = (
    ('Small Animals', 'SMALL ANIMALS'),
    ('Large Animals', 'LARGE ANIMALS'),
    ('Poultry', 'Poultry'),
)

SALUTATION_CHOICES = (
    ('Dr', 'DOCTOR'),
    ('Prof', 'PROFESSOR')
)

SATISFACTION_CHOICES = (
    ('Satisfied', 'SATISFIED'),
    ('Not Satisfied', 'NOT SATISFIED')
)

SERVICES_CHOICES = (
    ('Consultation', 'CONSULTATION'),
    ('Surgery', "SURGERY"),
    ('Clinical Services', 'CLINICAL SERVICES'),
    ('Obstetrical Services', 'OBSTETRICAL SERVICES'),
    ('Nutrition Analysis', 'NUTRITION ANALYSIS'),
    ('Feed Formulation', 'FEED FORMULATION')
)

EDUCATION_QUALIFICATIONS_CHOICES = (
    ('K.C.P.E', 'K.C.P.E'),
    ('K.C.S.E', 'K.C.S.E'),
    ('CERTIFICATE', 'CERTIFICATE'),
    ('DIPLOMA', 'DIPLOMA'),
    ('DEGREE', 'DEGREE'),
    ('MASTERS DEGREE', 'MASTERS DEGREE'),
    ('Phd', 'Phd')
)

REQUEST_STATUS_CHOICES = (
    ('ACCEPTED', 'ACCEPTED'),
    ('REJECTED', 'REJECTED'),
    ('PENDING', 'PENDING')
)

CONSULTATION_STATUS_CHOICES = (
    ('PENDING', 'PENDING'),
    ('ACCEPTED', 'ACCEPTED'),
    ('IN_PROGRESS', 'IN_PROGRESS'),
    ('COMPLETED', 'COMPLETED'),
    ('CANCELLED', 'CANCELLED'),
    ('REJECTED', 'REJECTED')
)

APPOINTMENT_STATUS_CHOICES = (
    ('PENDING', 'PENDING'),
    ('ACCEPTED', 'ACCEPTED'),
    ('REJECTED', 'REJECTED'),
    ('COMPLETED', 'COMPLETED'),
    ('CANCELLED', 'CANCELLED'),
)

COUNTY_CHOICES = (
    ('Mombasa', 'MOMBASA'),
    ('Nairobi', 'NAIROBI'),
    ('Trans-Nzoia', 'TRANS-NZOIA'),
    ('West Pokot', 'WEST POKOT'),
    ('Marakwet', 'MARAKWET'),
    ('Isiolo', 'ISIOLO'),
    ('Kericho', 'KERICHO'),
    ('Uasin-Gishu', 'UASIN-GISHU')
)

TOWN_CHOICES = (
    ('Kitale', 'KITALE'),
    ('Eldoret', 'ELDORET'),
    ('Mombasa', 'Mombasa'),
    ('Nairobi', 'NAIROBI'),
    ('Kericho', 'KERICHO'),
    ('Kapenguria', 'KAPENGURIA'),
    ('Iten', 'ITEN'),
    ('Isiolo', 'ISIOLO'),
)

SEX_CHOICES = (
    ('M', 'MALE'),
    ('F', 'FEMALE')
)

PAYMENT_STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('PAID', 'Paid'),
    ('REFUNDED', 'Refunded'),
    ('CANCELLED', 'Cancelled'),
)

AUDIT_ACTION_CHOICES = (
    ('CREATE', 'Create'),
    ('UPDATE', 'Update'),
    ('DELETE', 'Delete'),
    ('STATUS_CHANGE', 'Status Change'),
)

NOTIFICATION_CATEGORY_CHOICES = (
    ('COLLEAGUE', 'Colleague Request'),
    ('APPOINTMENT', 'Appointment'),
    ('CONSULTATION', 'Consultation'),
    ('RATING', 'Rating/Review'),
    ('SYSTEM', 'System'),
)

DAY_OF_WEEK_CHOICES = (
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
)
