from .base import *
from .base import _BaseApplicationForm


class VolunteerApplicationForm(_BaseApplicationForm):


    diet = forms.ChoiceField(
        required=True,
        label='Restricciones alimentarias',
        choices=models.DIETS_ES,
        help_text="Estas son las diferentes opciones que tenemos. No podemos asegurar que la carne sea hallal."
    )

    first_timer = forms.BooleanField(
        required=False, initial=False, widget=forms.HiddenInput
    )
    first_time_volunteer = forms.TypedChoiceField(
        required=True,
        label="¿Es tu primera vez haciendo voluntariado en %s?" % settings.HACKATHON_NAME,
        coerce=lambda x: x == "True",
        choices=((True, "Sí"), (False, "No")),
        widget=forms.RadioSelect,
    )
    which_hack = forms.MultipleChoiceField(
        required=False,
        label="¿En qué ediciones de %s has participado como voluntari@?" % settings.HACKATHON_NAME,
        widget=forms.CheckboxSelectMultiple,
        choices=models.PREVIOUS_HACKS,
    )
    under_age = forms.TypedChoiceField(
        required=True,
        label="¿Tienes o tendrás la mayoría de edad antes de la fecha del evento?",
        initial=False,
        coerce=lambda x: x == "True",
        choices=((False, "No"), (True, "Sí")),
        widget=forms.RadioSelect,
    )
    night_shifts = forms.TypedChoiceField(
        required=True,
        label="¿Estarias de acuerdo en seguir ayudando pasado medianoche?",
        coerce=lambda x: x == "True",
        choices=((False, "No"), (True, "Sí"), (None, "Puede ser")),
        help_text="No exigimos a nadie quedarse hasta ninguna hora en particular",
        widget=forms.RadioSelect,
    )
    lennyface = forms.CharField(initial="NA", widget=forms.HiddenInput(), required=False)

    hear_about_us = forms.TypedChoiceField(
        required=True,
        label="¿Cómo nos has conocido?",
        choices=models.HEARABOUTUS_ES,
        widget=forms.RadioSelect,
    )

    university = forms.CharField(
        initial="NA", widget=forms.HiddenInput(), required=False
    )

    degree = forms.CharField(initial="NA", widget=forms.HiddenInput(), required=False)

    terms_and_conditions = forms.BooleanField(
        required=False,
        label='He leído, entendido y acepto los <a href="/terms_and_conditions" target="_blank">%s '
              'Términos y Condiciones</a> '
              'y la <a href="/privacy_and_cookies" '
              'target="_blank">%s Política de Privacidad y Cookies'
              '</a>.<span style="color: red; font-weight: bold;"> '
              '*</span>' % (settings.HACKATHON_NAME, settings.HACKATHON_NAME)
              )

    email_subscribe = forms.BooleanField(required=False, label='Suscríbete a nuestra lista de marketing para informarte sobre nuestros próximos eventos.')

    diet_notice = forms.BooleanField(
        required=False,
        label='Autorizo a "HackersAtUpc" a utilizar mi información sobre alergias e intolerancias alimentarias únicamente para gestionar el servicio de catering.<span style="color: red; font-weight: bold;"> *</span>'
    )

    bootstrap_field_info = {
        "Información Personal": {
            "fields": [
                {"name": "pronouns", "space": 12},
                {"name": "gender", "space": 12},
                {"name": "other_gender", "space": 12},
                {"name": "under_age", "space": 12},
                {"name": "hear_about_us", "space": 12},
                {"name": "origin", "space": 12},
            ],
            "description": "Hola voluntari@, necesitamos un poco de información antes de empezar :)",
        },
        "Voluntariado": {
            "fields": [
                {"name": "first_time_volunteer", "space": 12},
                {"name": "which_hack", "space": 12},
                {"name": "languages", "space": 12},
                {"name": "attendance", "space": 12},
                {"name": "volunteer_motivation", "space": 12},
            ],
        },
        "Otras preguntas": {
            "fields": [
                {"name": "friends", "space": 12},
                {"name": "night_shifts", "space": 12},
                {"name": "tshirt_size", "space": 12},
            ],
            "description": "¡No te asustes! Solo quedan algunas preguntas más 🤯",
        },
        "Intereses Personales": {
            "fields": [
                {"name": "fav_movie", "space": 12},
                {"name": "quality", "space": 12},
                {"name": "weakness", "space": 12},
                {"name": "hobbies", "space": 12},
                {"name": "cool_skill", "space": 12},
                # Hidden
                {"name": "graduation_year", "space": 12},
                {"name": "university", "space": 12},
                {"name": "degree", "space": 12},
            ],
            "description": "¡Queremos conocerte!",
        },
    }

    def clean(self):
        volunteer = self.cleaned_data["first_time_volunteer"]
        if not volunteer:
            data = self.cleaned_data["which_hack"]
            self.add_error("which_hack", "Choose the hackathons you volunteered")

        return super(VolunteerApplicationForm, self).clean()


    def volunteer(self):
        return True

    def clean_reimb_amount(self):
        data = self.cleaned_data["reimb_amount"]
        reimb = self.cleaned_data.get("reimb", False)
        if reimb and not data:
            raise forms.ValidationError(
                "To apply for reimbursement please set a valid amount"
            )
        deadline = getattr(settings, "REIMBURSEMENT_DEADLINE", False)
        if data and deadline and deadline <= timezone.now():
            raise forms.ValidationError(
                "Reimbursement applications are now closed. Trying to hack us?"
            )
        return data

    def clean_reimb(self):
        reimb = self.cleaned_data.get("reimb", False)
        deadline = getattr(settings, "REIMBURSEMENT_DEADLINE", False)
        if reimb and deadline and deadline <= timezone.now():
            raise forms.ValidationError(
                "Reimbursement applications are now closed. Trying to hack us?"
            )
        return reimb

    def get_bootstrap_field_info(self):
        fields = super().get_bootstrap_field_info()
        discord = getattr(settings, "DISCORD_HACKATHON", False)
        other_fields = fields["Otras preguntas"]["fields"]
        polices_fields = [
            {"name": "terms_and_conditions", "space": 12},
            {"name": "email_subscribe", "space": 12},
        ]
        if not discord:
            other_fields.extend(
                [
                    {"name": "diet", "space": 12},
                    {"name": "other_diet", "space": 12},
                ]
            )
            polices_fields.append({"name": "diet_notice", "space": 12})
        # Fields that we only need the first time the hacker fills the application
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not self.instance.pk:
            fields["Políticas HackUPC"] = {
                "fields": polices_fields,
                "description": '<p style="color: margin-top: 1em;display: block;'
                'margin-bottom: 1em;line-height: 1.25em;">Nosotros, Hackers at UPC, '
                "procesamos tu información para organizar la mejor hackathon posible. "
                "También incluirá imágenes y videos tuyos durante el evento. "
                "Tus datos se utilizarán principalmente para admisiones. También podríamos contactarte  "
                "(enviándote un correo electrónico) sobre otros eventos que estamos organizando y"
                "que son de una naturaleza similar a los que previamente solicitaste. Para más"
                "información sobre el procesamiento de tus datos personales y sobre cómo ejercer tus"
                "derechos de acceso, rectificación, supresión, limitación, portabilidad y oposición, por"
                "favor visita nuestra Política de Privacidad y Cookies.</p>",
            }
        return fields

    class Meta(_BaseApplicationForm.Meta):
        model = models.VolunteerApplication
        help_texts = {
            "degree": "What's your major/degree?",
            "other_diet": "Porfavor indica tus restricciones alimentarias. ¡Queremos assegurarnos que tenemos comida para ti!",
            "attendance": "Será una gran experiencia disfrutar de principio a fin con muchas cosas que hacer, pero está bien si no puedes venir todo el fin de semana",
            "languages": "No se necesita nivel de inglés para ser voluntari@, solo queremos comprobar quién se sentiría cómod@ realizando tareas que requieran comunicación en inglés",
            "fav_movie": "e.g.: Interstellar, Juego de Tronos,  Avatar, La Casa de Papel, etc.",
            "cool_skill": "Las 3 respuestas más originales tendrán un pequeño premio que se entregará en el 2º encuentro de voluntarios 😛",
            "friends": "Recuerda que todos tienen que aplicar por separado",
            "origin": "Ejemplo: Barcelona, Lleida",
            "volunteer_motivation": "¡Puede ser una respuesta corta, solo tenemos curiosidad 😛!",
        }

        widgets = {
            "origin": forms.TextInput(attrs={"autocomplete": "off"}),
            "languages": forms.CheckboxSelectMultiple(),
            "friends": forms.Textarea(attrs={"rows": 2, "cols": 40}),
            "weakness": forms.Textarea(attrs={"rows": 2, "cols": 40}),
            "quality": forms.Textarea(attrs={"rows": 2, "cols": 40}),
            "hobbies": forms.Textarea(attrs={"rows": 2, "cols": 40}),
            "pronouns": forms.TextInput(
                attrs={"autocomplete": "off", "placeholder": "their/them"}
            ),
            "graduation_year": forms.HiddenInput(),
            "phone_number": forms.HiddenInput(),
            "hear_about_us": forms.RadioSelect(),
        }

        labels = {
            "pronouns": "¿Cuáles son tus pronombres?",
            "gender": " ¿Con qué género te identificas?",
            "other_gender": "Me quiero describir",
            "graduation_year": "What year will you graduate?",
            "tshirt_size": "¿Cuál es tu talla de camiseta?",
            "diet": "Restricciones alimentarias",
            "origin": "¿Cuál es tu lugar de residencia actual?",
            "which_hack": "¿En qué ediciones de %s has participado como voluntari@?" % settings.HACKATHON_NAME,
            "attendance": "¿Qué días asistirás a HackUPC?",
            "languages": "¿En qué idiomas te sientes cómod@ hablando?",
            "quality": "Nombra una cualidad tuya:",
            "weakness": "Ahora un punto débil:",
            "cool_skill": "¿Qué habilidad interesante o dato curioso tienes? ¡Sorpréndenos! 🎉",
            "fav_movie": " ¿Cuál es tu película o serie favorita?",
            "friends": "¿Estás aplicando con otr@s amig@s? Escribe sus nombres completos",
            "hobbies": "¿Cuáles son tus hobbies o qué haces en tu tiempo libre?",
            "volunteer_motivation": "¿Por qué quieres asistir como voluntari@ a HackUPC?",
        }


