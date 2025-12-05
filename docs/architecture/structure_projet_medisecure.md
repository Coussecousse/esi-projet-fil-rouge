## Structure du projet : 

### Structure du back en fastAPI : 

medisecure-backend/
├── api/
│   ├── __init__.py
│   ├── main.py                         # Point d'entrée FastAPI
│   ├── handlers/
│   │   └── exception_handlers.py       # Gestionnaires d'exceptions pour FastAPI
│   ├── middlewares/
│   │   └── authentication_middleware.py # Middleware d'authentification
│   └── routers/
│       ├── patient_router.py           # Router FastAPI pour les patients
│       ├── appointment_router.py       # Router FastAPI pour les rendez-vous
│       └── medical_records_router.py   # Router FastAPI pour les dossiers médicaux
│
├── patient_management/                 # Bounded Context: Gestion des patients
│   ├── __init__.py
│   ├── application/
│   │   ├── __init__.py
│   │   ├── dtos/
│   │   │   └── patient_dtos.py         # DTOs pour patients
│   │   └── usecases/
│   │       ├── create_patient_folder_usecase.py   # Créer un dossier patient
│   │       └── update_patient_usecase.py          # Mettre à jour un patient
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   └── patient.py              # Entité Patient
│   │   ├── exceptions/
│   │   │   ├── missing_guardian_consent.py
│   │   │   ├── missing_patient_consent.py
│   │   │   ├── missing_required_field.py
│   │   │   ├── patient_already_exists.py
│   │   │   └── patient_not_found.py
│   │   ├── ports/
│   │   │   ├── primary/
│   │   │   └── secondary/
│   │   │       └── patient_repository_protocol.py   # Port pour le repository
│   │   └── services/
│   │       └── patient_service.py      # Service de domaine pour les patients
│   └── infrastructure/
│       ├── __init__.py
│       └── adapters/
│           ├── primary/
│           │   └── controllers/
│           │       └── patient_controller.py   # Controlleur pour l'API patient
│           └── secondary/
│               ├── postgres_patient_repository.py   # Implementation PostgreSQL
│               └── in_memory_patient_repository.py  # Implementation mémoire pour tests
│
├── appointment_management/             # Bounded Context: Gestion des rendez-vous
│   ├── __init__.py
│   ├── application/
│   │   ├── __init__.py
│   │   ├── dtos/
│   │   │   └── appointment_dtos.py
│   │   └── usecases/
│   │       ├── schedule_appointment_usecase.py
│   │       └── cancel_appointment_usecase.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── appointment.py
│   │   │   └── calendar.py
│   │   ├── exceptions/
│   │   │   └── appointment_exceptions.py
│   │   ├── ports/
│   │   │   ├── primary/
│   │   │   └── secondary/
│   │   │       └── appointment_repository_protocol.py
│   │   └── services/
│   │       └── appointment_service.py
│   └── infrastructure/
│       ├── __init__.py
│       └── adapters/
│           ├── primary/
│           │   └── controllers/
│           │       └── appointment_controller.py
│           └── secondary/
│               ├── postgres_appointment_repository.py   # Implementation PostgreSQL
│               └── in_memory_appointment_repository.py  # Implementation pour tests
│
├── medical_records/                    # Bounded Context: Dossiers médicaux
│   ├── __init__.py
│   ├── application/
│   │   ├── __init__.py
│   │   ├── dtos/
│   │   │   └── medical_record_dtos.py
│   │   └── usecases/
│   │       └── add_document_usecase.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── document.py
│   │   │   ├── lab_result.py
│   │   │   └── prescription.py
│   │   ├── exceptions/
│   │   │   └── medical_record_exceptions.py
│   │   ├── ports/
│   │   │   ├── primary/
│   │   │   └── secondary/
│   │   │       └── document_repository_protocol.py
│   │   └── services/
│   │       └── medical_record_service.py
│   └── infrastructure/
│       ├── __init__.py
│       └── adapters/
│           ├── primary/
│           │   └── controllers/
│           │       └── medical_record_controller.py
│           └── secondary/
│               ├── postgres_document_repository.py   # Implementation PostgreSQL
│               └── in_memory_document_repository.py  # Implementation mémoire pour tests
│
├── shared/                             # Éléments partagés entre les bounded contexts
│   ├── __init__.py
│   ├── application/
│   │   ├── __init__.py
│   │   └── dtos/
│   │       └── common_dtos.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   └── user.py                # Entité utilisateur partagée
│   │   ├── enums/
│   │   │   └── roles.py              # Enum des rôles d'utilisateurs
│   │   └── exceptions/
│   │       └── shared_exceptions.py
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py         # Configuration de la connexion PostgreSQL
│   │   │   └── models/               # Modèles SQLAlchemy
│   │   │       ├── __init__.py
│   │   │       ├── patient_model.py
│   │   │       ├── appointment_model.py
│   │   │       └── user_model.py
│   │   └── services/
│   │       └── smtp_mailer.py        # Service d'envoi d'emails
│   ├── ports/
│   │   ├── primary/
│   │   │   ├── authenticator_protocol.py
│   │   │   └── id_generator_protocol.py
│   │   └── secondary/
│   │       ├── mailer_protocol.py
│   │       └── user_repository_protocol.py
│   ├── adapters/
│   │   ├── primary/
│   │   │   ├── fixed_id_generator.py   # Générateur d'ID fixe pour tests
│   │   │   └── uuid_generator.py       # Générateur d'ID avec UUID
│   │   └── secondary/
│   │       ├── postgres_user_repository.py   # Implementation PostgreSQL
│   │       └── in_memory_user_repository.py  # Implementation mémoire pour tests
│   ├── services/
│   │   └── authenticator/
│   │       ├── basic_authenticator.py
│   │       └── extract_token.py
│   └── container/
│       └── container.py               # Container d'injection de dépendances avec dependency-injector
│
├── alembic/                           # Migrations de base de données avec Alembic
│   ├── versions/
│   │   └── ...                        # Fichiers de migration
│   ├── env.py
│   └── alembic.ini
│
├── tests/                              # Tests pour toute l'application
│   ├── __init__.py
│   ├── e2e/                           # Tests end-to-end avec TestClient de FastAPI
│   │   ├── __init__.py
│   │   ├── test_create_patient_folder.py
│   │   └── test_schedule_appointment.py
│   ├── integration/                    # Tests d'intégration
│   │   ├── __init__.py
│   │   └── test_postgres_patient_repository.py
│   └── unit/                           # Tests unitaires
│       ├── __init__.py
│       ├── patient_management/
│       │   ├── __init__.py
│       │   └── test_create_patient_folder.py
│       └── shared/
│           ├── __init__.py
│           └── test_basic_authenticator.py
│
├── pyproject.toml                     # Configuration du projet (dépendances, etc.)
├── requirements.txt                   # Dépendances du projet
├── .env                               # Variables d'environnement
├── .env.example                       # Exemple de variables d'environnement
├── .gitignore                         # Fichiers à ignorer par Git
├── Dockerfile                         # Configuration Docker
└── docker-compose.yml                 # Configuration Docker Compose (FastAPI + PostgreSQL)
```

## Pour le frontend avec React:


medisecure-frontend/
├── public/
│   ├── index.html
│   ├── favicon.ico
│   └── manifest.json
├── src/
│   ├── assets/
│   │   ├── images/
│   │   ├── icons/
│   │   └── styles/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.jsx
│   │   │   ├── Card.jsx
│   │   │   ├── Input.jsx
│   │   │   └── Modal.jsx
│   │   ├── layout/
│   │   │   ├── Header.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   └── Footer.jsx
│   │   ├── patients/
│   │   │   ├── PatientForm.jsx
│   │   │   ├── PatientCard.jsx
│   │   │   └── PatientList.jsx
│   │   ├── appointments/
│   │   │   ├── AppointmentForm.jsx
│   │   │   ├── Calendar.jsx
│   │   │   └── AppointmentList.jsx
│   │   └── medical-records/
│   │       ├── MedicalRecordView.jsx
│   │       └── DocumentUpload.jsx
│   ├── contexts/
│   │   ├── AuthContext.jsx
│   │   └── ThemeContext.jsx
│   ├── pages/
│   │   ├── auth/
│   │   │   ├── Login.jsx
│   │   │   └── ResetPassword.jsx
│   │   ├── patients/
│   │   │   ├── PatientListPage.jsx
│   │   │   ├── PatientDetailsPage.jsx
│   │   │   └── CreatePatientPage.jsx
│   │   ├── appointments/
│   │   │   ├── AppointmentCalendarPage.jsx
│   │   │   └── CreateAppointmentPage.jsx
│   │   ├── medical-records/
│   │   │   └── MedicalRecordPage.jsx
│   │   ├── Dashboard.jsx
│   │   └── NotFound.jsx
│   ├── services/
│   │   ├── api.js
│   │   ├── authService.js
│   │   ├── patientService.js
│   │   ├── appointmentService.js
│   │   └── medicalRecordService.js
│   ├── utils/
│   │   ├── formatters.js
│   │   ├── validators.js
│   │   └── constants.js
│   ├── hooks/
│   │   ├── useAuth.js
│   │   ├── useFetch.js
│   │   └── useForm.js
│   ├── App.jsx
│   ├── index.jsx
│   └── routes.js
├── package.json
├── tailwind.config.js                 # Configuration Tailwind CSS
├── .eslintrc.js                       # Configuration ESLint
├── .prettierrc                        # Configuration Prettier
├── .env                               # Variables d'environnement pour le frontend
├── .env.development                   # Variables d'environnement pour le développement
├── .env.production                    # Variables d'environnement pour la production
├── tsconfig.json                      # Configuration TypeScript (si vous utilisez TS)
├── vite.config.js                     # Configuration Vite (si vous utilisez Vite)
└── README.md


Cette structure respecte l'architecture hexagonale pour le backend FastAPI avec PostgreSQL et utilise une organisation modulaire basée sur les fonctionnalités pour le frontend React.