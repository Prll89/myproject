from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password


class Study(models.Model):
    estado = models.CharField(max_length=50, choices=[
        ('Pendiente', 'Pendiente'),
        ('Entregado', 'Entregado'),
        ('Desestimado', 'Desestimado'),
        ('Aceptado', 'Aceptado'),
        ('Rechazado', 'Rechazado'),
    ], default='Pendiente')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expediente = models.CharField(max_length=100)
    project_name = models.CharField(max_length=255)
    due_date = models.DateTimeField()
    
    def __str__(self):
        return f"{self.expediente} - {self.project_name}"

class ProcessingSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.id} - {self.processed_at}"

class ProcessedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    processing_session = models.ForeignKey(
        ProcessingSession,
        on_delete=models.CASCADE,
        related_name='processed_files',
        null=False,  # Allow null values temporarily
    )
    original_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='processed_files/')
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_name

class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relaciona el contacto con el usuario
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    gremio = models.TextField(blank=True, null=True)  # Permitir múltiples valores
    
    def __str__(self):
        return self.name

class EmailAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relaciona la cuenta con el usuario
    email = models.EmailField(unique=True)
    smtp_server = models.CharField(max_length=255)
    smtp_port = models.IntegerField()
    smtp_username = models.CharField(max_length=255)
    smtp_password = models.CharField(max_length=255)

    def __str__(self):
        return self.email
    
class EmailDraft(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    from_email = models.EmailField()
    recipients = models.ManyToManyField('Contact')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_draft = models.BooleanField(default=True)

    def __str__(self):
        return self.subject

class SentEmail(models.Model):
    EMAIL_TYPE_CHOICES = [
        ('Envío', 'Envío'),
        ('Reclamo', 'Reclamo'),
        # Puedes agregar otros tipos si es necesario
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    from_email = models.EmailField()
    to_emails = models.TextField()
    to_names = models.TextField(null=True, blank=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    study = models.ForeignKey(Study, on_delete=models.CASCADE, null=True, blank=True)
    files = models.ManyToManyField(ProcessedFile)
    email_type = models.CharField(max_length=20, choices=EMAIL_TYPE_CHOICES, default='Envío')  # Nuevo campo

    def __str__(self):
        return f"{self.subject} - {self.to_emails}"
    
class ProcessedFileContactStatus(models.Model):
    STATUS_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Reclamado', 'Reclamado'),
        ('Recibido', 'Recibido'),
        ('Rechazado', 'Rechazado'),
    ]

    processed_file = models.ForeignKey(ProcessedFile, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendiente')
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha y hora de creación
    updated_at = models.DateTimeField(auto_now=True)   

    class Meta:
        unique_together = ('processed_file', 'contact')

    def __str__(self):
        return f"{self.contact.name} - {self.processed_file.original_name} - {self.status}"
    
class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    study = models.ForeignKey(Study, on_delete=models.CASCADE, null=True, blank=True)  # Permitir null y blank
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"{self.title} ({self.start_date} - {self.end_date})"

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Nombre comercial
    legal_name = models.CharField(max_length=255, null=True, blank=True)  # Nombre legal de la empresa
    tax_id = models.CharField(max_length=50, null=True, blank=True)  # NIF/CIF/VAT
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    company_password_hash = models.CharField(max_length=128)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)

    def set_password(self, raw_password):
        self.company_password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.company_password_hash)

    def __str__(self):
        return self.name
    
    def departments(self):
        return self.department_set.all()
    
class Department(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.company.name}"

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN_TOTAL', 'Administrador Total'),
        ('ADMIN_DEPARTAMENTO', 'Administrador de Departamento'),
        ('TECNICO_DEPARTAMENTO', 'Técnico de Departamento'),
        # Añade más roles según sea necesario
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"