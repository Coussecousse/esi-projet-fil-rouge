from shared.domain.exceptions.shared_exceptions import DomainException

class PatientNotFoundException(DomainException):
    """Exception levée lorsqu'un patient n'est pas trouvé"""
    def __init__(self, patient_id):
        self.patient_id = patient_id
        message = f"Patient with ID {patient_id} not found"
        super().__init__(message)

class PatientAlreadyExistsException(DomainException):
    """Exception levée lorsqu'un patient existe déjà"""
    def __init__(self, identifier_type, identifier_value):
        self.identifier_type = identifier_type
        self.identifier_value = identifier_value
        message = f"Patient with {identifier_type} {identifier_value} already exists"
        super().__init__(message)

class MissingPatientConsentException(DomainException):
    """Exception levée lorsque le consentement du patient est manquant"""
    def __init__(self, patient_id):
        self.patient_id = patient_id
        message = f"Patient with ID {patient_id} has not given consent"
        super().__init__(message)

class MissingRequiredFieldException(DomainException):
    """Exception levée lorsqu'un champ requis est manquant"""
    def __init__(self, field_name):
        self.field_name = field_name
        message = f"Required field {field_name} is missing"
        super().__init__(message)

class MissingGuardianConsentException(DomainException):
    """Exception levée lorsque le consentement du tuteur légal est manquant pour un mineur"""
    def __init__(self, patient_id):
        self.patient_id = patient_id
        message = f"Guardian consent is required for minor patient with ID {patient_id}"
        super().__init__(message)