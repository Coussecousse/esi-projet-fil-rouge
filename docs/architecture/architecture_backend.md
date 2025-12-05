```mermaid
graph TB
    %% Définition des styles
    classDef domainStyle fill:#f9f7ed,stroke:#8b7355,color:#000
    classDef applicationStyle fill:#ebf8ff,stroke:#3182ce,color:#000
    classDef portStyle fill:#edf7ed,stroke:#38a169,color:#000
    classDef adapteurStyle fill:#faf0e6,stroke:#d97706,color:#000
    classDef infraStyle fill:#f0e6fa,stroke:#805ad5,color:#000

    %% Couche Domaine (Hexagone central)
    subgraph Domaine
        entites["Entités<br/>(Patient, Appointment, User)"]
        services["Services Métier<br/>(PatientService, AppointmentService)"]
        exceptions["Exceptions Métier<br/>(PatientNotFoundException, etc.)"]
        enums["Enums<br/>(UserRole, AppointmentStatus)"]
    end

    %% Couche Application (Use Cases)
    subgraph Application
        usecases["Use Cases<br/>(CreatePatientUseCase,<br/>GetPatientUseCase, etc.)"]
        dtos["DTOs<br/>(PatientCreateDTO, PatientResponseDTO, etc.)"]
    end

    %% Ports Primaires (Interfaces Used by Adapters)
    subgraph PortsPrimaires["Ports Primaires (Driving/Left)"]
        idGeneratorProtocol["IdGeneratorProtocol"]
        authenticatorProtocol["AuthenticatorProtocol"]
    end

    %% Ports Secondaires (Interfaces Used by Domain)
    subgraph PortsSecondaires["Ports Secondaires (Driven/Right)"]
        patientRepositoryProtocol["PatientRepositoryProtocol"]
        appointmentRepositoryProtocol["AppointmentRepositoryProtocol"]
        userRepositoryProtocol["UserRepositoryProtocol"]
        mailerProtocol["MailerProtocol"]
    end

    %% Adaptateurs Primaires (Driving Adapters)
    subgraph AdaptateursPrimaires["Adaptateurs Primaires (Driving/Left)"]
        controllers["Controllers<br/>(PatientController, AuthController)"]
        middleware["Middleware<br/>(AuthenticationMiddleware)"]
        uuidGenerator["UuidGenerator"]
        basicAuthenticator["BasicAuthenticator"]
    end

    %% Adaptateurs Secondaires (Driven Adapters)
    subgraph AdaptateursSecondaires["Adaptateurs Secondaires (Driven/Right)"]
        postgresRepositories["Repositories PostgreSQL<br/>(PostgresPatientRepository, etc.)"]
        inMemoryRepositories["Repositories In-Memory<br/>(InMemoryPatientRepository, etc.)"]
        smtpMailer["SmtpMailer"]
    end

    %% Infrastructure
    subgraph Infrastructure
        dbModels["Modèles DB<br/>(UserModel, PatientModel, etc.)"]
        connectionDB["Connection DB<br/>(SQLAlchemy)"]
        container["Container<br/>(Dependency Injection)"]
    end

    %% Relations entre les composants
    entites --> services
    services --> exceptions
    entites --> enums
    
    dtos --> usecases
    usecases --> services
    
    PortsPrimaires --> Application
    Application --> PortsSecondaires
    
    AdaptateursPrimaires --> PortsPrimaires
    PortsSecondaires --> AdaptateursSecondaires
    
    AdaptateursSecondaires --> Infrastructure
    
    %% Direction des dépendances pour l'architecture hexagonale
    AdaptateursPrimaires -.-> Application
    Application -.-> Domaine
    AdaptateursSecondaires -.-> PortsSecondaires
    PortsSecondaires -.-> Domaine
    
    %% Appliquer les styles
    class entites,services,exceptions,enums domainStyle
    class usecases,dtos applicationStyle
    class idGeneratorProtocol,authenticatorProtocol,patientRepositoryProtocol,appointmentRepositoryProtocol,userRepositoryProtocol,mailerProtocol portStyle
    class controllers,middleware,uuidGenerator,basicAuthenticator,postgresRepositories,inMemoryRepositories,smtpMailer adapteurStyle
    class dbModels,connectionDB,container infraStyle
```

Le diagramme ci-dessus illustre l'architecture hexagonale (également appelée architecture ports et adaptateurs) utilisée dans le backend MediSecure. Voici une explication détaillée des différentes couches:

### Structure Hexagonale

1. **Couche Domaine (Cœur)** - Le centre de l'hexagone:
   - **Entités**: Patient, Appointment, User - objets de valeur fondamentaux avec leur logique métier
   - **Services métier**: PatientService, AppointmentService - implémentent les règles métier complexes
   - **Exceptions métier**: PatientNotFoundException, etc. - exceptions spécifiques au domaine
   - **Enums**: UserRole, AppointmentStatus - types énumérés du domaine

2. **Couche Application**:
   - **Use Cases**: CreatePatientUseCase, GetPatientUseCase, etc. - orchestrent les opérations du domaine
   - **DTOs**: PatientCreateDTO, PatientResponseDTO - objets de transfert de données

3. **Ports** - Interfaces qui définissent comment les adaptateurs interagissent avec le domaine:
   - **Ports Primaires** (driving/left side): IdGeneratorProtocol, AuthenticatorProtocol
   - **Ports Secondaires** (driven/right side): PatientRepositoryProtocol, UserRepositoryProtocol, etc.

4. **Adaptateurs** - Implémentations concrètes qui connectent le système aux technologies externes:
   - **Adaptateurs Primaires**: Controllers, Middleware, UuidGenerator
   - **Adaptateurs Secondaires**: PostgresRepositories, InMemoryRepositories, SmtpMailer

5. **Infrastructure**:
   - Modèles de base de données (UserModel, PatientModel)
   - Connection DB via SQLAlchemy
   - Container pour l'injection de dépendances

### Avantages de cette architecture

- **Isolation du domaine**: Le code métier est protégé des détails techniques
- **Testabilité**: Facilité de tester en remplaçant les adaptateurs (ex: repositories in-memory pour les tests)
- **Flexibilité**: Les adaptateurs externes peuvent être changés sans affecter le domaine
- **Indépendance des frameworks**: Le domaine ne dépend d'aucun framework
