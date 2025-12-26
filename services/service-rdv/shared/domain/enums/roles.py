from enum import Enum

class UserRole(str, Enum):
    """Enumération des rôles d'utilisateurs dans le système"""
    ADMIN = "ADMIN" 
    DOCTOR = "DOCTOR"
    NURSE = "NURSE"
    PATIENT = "PATIENT"
    RECEPTIONIST = "RECEPTIONIST"