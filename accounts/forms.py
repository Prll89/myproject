from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Study, Contact, EmailAccount, ProcessedFile, Event, Department, UserProfile, Company
from tinymce.widgets import TinyMCE
from django.forms.widgets import DateTimeInput
from .models import Company


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class UploadFileForm(forms.Form):
    ACTION_CHOICES = [
        ('process_measurements', 'Procesar Mediciones'),
        ('upload_packages', 'Subir Paquetes'),
    ]
    
    study = forms.ModelChoiceField(
        queryset=Study.objects.none(),
        required=True,
        label='Seleccionar Estudio',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True,
        label='Seleccione Acción'
    )
    
    start_column = forms.CharField(
        max_length=2,
        required=False,
        label='Columna de Inicio',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ejemplo: F'
        })
    )
    
    end_column = forms.CharField(
        max_length=2,
        required=False,
        label='Columna de Fin',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ejemplo: J'
        })
    )
    
    file_excel = forms.FileField(
        required=False,
        label='Archivo Excel',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xlsm,.xltx,.xltm'
        })
    )
    
    file_zip = forms.FileField(
        required=False,
        label='Archivo ZIP',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.zip'
        })
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UploadFileForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['study'].queryset = Study.objects.filter(user=user)

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')

        if action == 'process_measurements':
            if not cleaned_data.get('start_column'):
                self.add_error('start_column', 'Este campo es requerido para procesar mediciones.')
            if not cleaned_data.get('end_column'):
                self.add_error('end_column', 'Este campo es requerido para procesar mediciones.')
            file_excel = cleaned_data.get('file_excel')
            if not file_excel:
                self.add_error('file_excel', 'Por favor, suba un archivo Excel válido.')
            elif not file_excel.name.endswith(('.xlsx', '.xlsm', '.xltx', '.xltm')):
                self.add_error('file_excel', 'Por favor, suba un archivo Excel válido.')
        elif action == 'upload_packages':
            file_zip = cleaned_data.get('file_zip')
            if not file_zip:
                self.add_error('file_zip', 'Por favor, suba un archivo ZIP válido.')
            elif not file_zip.name.endswith('.zip'):
                self.add_error('file_zip', 'Por favor, suba un archivo ZIP válido.')
        else:
            self.add_error('action', 'Acción inválida seleccionada.')

        return cleaned_data
    
class StudyForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['expediente', 'project_name', 'due_date']  # Exclude 'estado'
        widgets = {
            'due_date': forms.DateInput(attrs={'class': 'form-control datetimepicker', 'type': 'text'}),
        }

    def __init__(self, *args, **kwargs):
        super(StudyForm, self).__init__(*args, **kwargs)
        # Apply 'form-control' class to each field
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'gremio']

class SendEmailForm(forms.Form):
    study = forms.ModelChoiceField(
        queryset=Study.objects.none(),
        required=True,
        label="Seleccionar Estudio",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    from_email = forms.ModelChoiceField(
        queryset=EmailAccount.objects.none(), 
        required=True,
        label="Desde",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    subject = forms.CharField(
        max_length=255,
        required=True,
        label="Asunto",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=True,
        label="Cuerpo"
    )
    cc = forms.CharField(
        required=False,
        label="En copia (CC)",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    bcc = forms.CharField(
        required=False,
        label="En copia oculta (BCC)",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(SendEmailForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['study'].queryset = Study.objects.filter(user=user).order_by('-expediente')
            self.fields['study'].label_from_instance = lambda obj: f"{obj.expediente} - {obj.project_name}"
            self.fields['from_email'].queryset = EmailAccount.objects.filter(user=user)
class EmailAccountForm(forms.ModelForm):
    class Meta:
        model = EmailAccount
        fields = ['email', 'smtp_server', 'smtp_port', 'smtp_username', 'smtp_password']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'smtp_server': forms.TextInput(attrs={'class': 'form-control'}),
            'smtp_port': forms.NumberInput(attrs={'class': 'form-control'}),
            'smtp_username': forms.TextInput(attrs={'class': 'form-control'}),
            'smtp_password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'email': 'Correo Electrónico',
            'smtp_server': 'Servidor SMTP',
            'smtp_port': 'Puerto SMTP',
            'smtp_username': 'Usuario SMTP',
            'smtp_password': 'Contraseña SMTP',
        }

class EventForm(forms.ModelForm):
    study_id = forms.ModelChoiceField(queryset=Study.objects.all(), required=False, label="Asignar a Estudio")
    
    class Meta:
        model = Event
        fields = ['study_id', 'title', 'start_date', 'end_date']
        labels = {
            'title': 'Título del Evento',
            'start_date': 'Fecha de Inicio',
            'end_date': 'Fecha de Finalización',
        }
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir la clase 'form-select' al campo de selección de estudio
        self.fields['study_id'].widget.attrs.update({'class': 'form-select'})
        # Asegurar que el campo 'title' tenga la clase 'form-control'
        self.fields['title'].widget.attrs.update({'class': 'form-control'})

class ReclamarEmailForm(forms.Form):
    from_email = forms.EmailField(label="De", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    subject = forms.CharField(label="Asunto", widget=forms.TextInput(attrs={'class': 'form-control'}))
    body = forms.CharField(label="Cuerpo del mensaje", widget=forms.Textarea(attrs={'class': 'form-control tinymce'}))
    cc = forms.CharField(label="Copia (CC)", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    bcc = forms.CharField(label="Copia Oculta (BCC)", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

class CompanyRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña de la Empresa'}),
        label='Contraseña de la Empresa'
    )

    class Meta:
        model = Company
        fields = [
            'name',
            'legal_name',
            'tax_id',
            'address',
            'city',
            'postal_code',
            'country',
            'contact_email',
            'contact_phone',
        ]
        labels = {
            'name': 'Nombre Comercial',
            'legal_name': 'Nombre Legal',
            'tax_id': 'NIF/CIF/VAT',
            'address': 'Dirección Fiscal',
            'city': 'Ciudad',
            'postal_code': 'Código Postal',
            'country': 'País',
            'contact_email': 'Correo Electrónico de Contacto',
            'contact_phone': 'Número de Teléfono',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre Comercial'}),
            'legal_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre Legal'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIF/CIF/VAT'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección Fiscal'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código Postal'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'País'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico de Contacto'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de Teléfono'}),
        }

    def save(self, commit=True):
        company = super().save(commit=False)
        password = self.cleaned_data['password']
        company.set_password(password)
        if commit:
            company.save()
        return company

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico'})
    )
    full_name = forms.CharField(
        max_length=255,
        label='Nombre Completo',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre Completo'})
    )
    company_name = forms.CharField(
        max_length=255,
        label='Nombre de la Empresa',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la Empresa'})
    )
    company_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña de la Empresa'}),
        label='Contraseña de la Empresa'
    )
    department_name = forms.CharField(
        max_length=255,
        label='Nombre del Departamento',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Departamento (Opcional)'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de Usuario'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar Contraseña'}),
        }

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de Usuario o Correo Electrónico'}),
        label='Nombre de Usuario o Correo Electrónico'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
        label='Contraseña'
    )
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput(), label='Recordarme')

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
        labels = {
            'name': 'Nombre',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Departamento'}),
        }

class ApproveUserForm(forms.Form):
    user_id = forms.IntegerField(widget=forms.HiddenInput())
    action = forms.ChoiceField(choices=[('approve', 'Aprobar'), ('decline', 'Rechazar')])

class ChangeRoleForm(forms.Form):
    user_id = forms.IntegerField(widget=forms.HiddenInput())
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)

class CompanyForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(),
        required=False,
        help_text='Deja este campo en blanco si no deseas cambiar la contraseña.'
    )
    password_confirm = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(),
        required=False
    )

    class Meta:
        model = Company
        fields = [
            'name',
            'legal_name',
            'tax_id',
            'address',
            'city',
            'postal_code',
            'country',
            'contact_email',
            'contact_phone',
            'stripe_customer_id',
            'password',
            'password_confirm',
        ]
        labels = {
            'name': 'Nombre Comercial',
            'legal_name': 'Nombre Legal',
            'tax_id': 'NIF/CIF/VAT',
            'address': 'Dirección',
            'city': 'Ciudad',
            'postal_code': 'Código Postal',
            'country': 'País',
            'contact_email': 'Correo de Contacto',
            'contact_phone': 'Teléfono de Contacto',
            'stripe_customer_id': 'ID de Cliente de Stripe',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre Comercial'}),
            'legal_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre Legal'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIF/CIF/VAT'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código Postal'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'País'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo de Contacto'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono de Contacto'}),
            'stripe_customer_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID de Cliente de Stripe'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password_confirm': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        # Solo validar las contraseñas si se proporcionaron (edición de empresa)
        if password or password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        company = super().save(commit=False)
        password = self.cleaned_data.get('password')

        if password:
            company.set_password(password)

        if commit:
            company.save()
        return company