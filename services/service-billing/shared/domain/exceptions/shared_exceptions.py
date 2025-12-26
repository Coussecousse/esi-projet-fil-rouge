class DomainException(Exception):
    """Exception de base pour toutes les exceptions du domaine"""
    pass

class EntityNotFoundException(DomainException):
    """Exception levée lorsqu'une entité n'est pas trouvée"""
    pass

class ValidationException(DomainException):
    """Exception levée lorsqu'une validation échoue"""
    pass

class AuthenticationException(DomainException):
    """Exception levée pour les problèmes d'authentification"""
    pass

class AuthorizationException(DomainException):
    """Exception levée pour les problèmes d'autorisation"""
    pass

class BusinessRuleException(DomainException):
    """Exception levée lorsqu'une règle métier est violée"""
    pass