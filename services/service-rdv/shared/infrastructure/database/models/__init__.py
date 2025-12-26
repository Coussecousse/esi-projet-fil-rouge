# shared/infrastructure/database/models/__init__.py
from shared.infrastructure.database.models.user_model import UserModel
from shared.infrastructure.database.models.patient_model import PatientModel
from shared.infrastructure.database.models.appointment_model import AppointmentModel

# Cet ordre est important pour résoudre les dépendances circulaires