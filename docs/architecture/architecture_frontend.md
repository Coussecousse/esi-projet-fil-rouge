```mermaid
graph TB
    %% Définition des styles
    classDef componentsStyle fill:#f9f7ed,stroke:#8b7355,color:#000
    classDef routingStyle fill:#ebf8ff,stroke:#3182ce,color:#000
    classDef apiStyle fill:#edf7ed,stroke:#38a169,color:#000
    classDef contextStyle fill:#faf0e6,stroke:#d97706,color:#000
    classDef pagesStyle fill:#f0e6fa,stroke:#805ad5,color:#000
    classDef utilitiesStyle fill:#f0f0e6,stroke:#555555,color:#000

    %% Composants de base (Core Components)
    subgraph Composants["Composants Réutilisables"]
        commonComponents["Composants Communs<br/>(Button, InputField, Alert, etc.)"]
        layoutComponents["Composants de Layout<br/>(Header, Sidebar, MainLayout)"]
        dataComponents["Composants de Données<br/>(DataTable, Pagination)"]
        appointmentComponents["Composants Métier<br/>(AppointmentCard)"]
        loadingComponent["Composant de Chargement<br/>(LoadingScreen)"]
    end

    %% Routage
    subgraph Routage
        routesDefinition["Routes<br/>(routes.tsx)"]
        navigation["Navigation<br/>(useNavigate, Link)"]
        routeGuards["Guards de Route<br/>(RequireAuth, RequireGuest)"]
    end

    %% API Services
    subgraph APIServices["Services API"]
        apiClient["API Client<br/>(apiClient.ts)"]
        endpoints["Endpoints<br/>(endpoints.ts)"]
        authService["Service Auth<br/>(authService.ts)"]
        patientService["Service Patient<br/>(patientService.ts)"]
        appointmentService["Service Appointment<br/>(appointmentService.ts)"]
    end

    %% Contextes
    subgraph Contextes
        authContext["Contexte Auth<br/>(AuthContext)"]
    end

    %% Pages
    subgraph Pages
        authPages["Pages Auth<br/>(LoginPage, ForgotPasswordPage)"]
        dashboardPage["Page Dashboard<br/>(DashboardPage)"]
        patientPages["Pages Patient<br/>(PatientsListPage, PatientDetailsPage,<br/>CreatePatientPage, EditPatientPage)"]
        appointmentPages["Pages Rendez-vous<br/>(AppointmentsCalendarPage, AppointmentDetailsPage,<br/>CreateAppointmentPage)"]
        medicalRecordsPages["Pages Dossiers Médicaux<br/>(MedicalRecordsPage, UploadDocumentPage)"]
        settingsPage["Page Paramètres<br/>(SettingsPage)"]
        notFoundPage["Page 404<br/>(NotFoundPage)"]
    end

    %% Types
    subgraph Types
        patientTypes["Types Patient<br/>(patient.types.ts)"]
    end

    %% App et Main
    appComponent["App<br/>(App.tsx)"]
    mainComponent["Main<br/>(main.tsx)"]

    %% Relations
    mainComponent --> appComponent
    appComponent --> Routage
    appComponent --> Contextes

    routesDefinition --> Pages
    Pages --> Composants
    Pages --> APIServices
    Pages --> Contextes
    
    authContext --> authService
    
    APIServices --> apiClient
    apiClient --> endpoints
    
    Composants --> Types
    Pages --> Types
    APIServices --> Types
    
    %% Appliquer les styles
    class commonComponents,layoutComponents,dataComponents,appointmentComponents,loadingComponent componentsStyle
    class routesDefinition,navigation,routeGuards routingStyle
    class apiClient,endpoints,authService,patientService,appointmentService apiStyle
    class authContext contextStyle
    class authPages,dashboardPage,patientPages,appointmentPages,medicalRecordsPages,settingsPage,notFoundPage pagesStyle
    class patientTypes utilitiesStyle
```

### Architecture du Frontend MediSecure

Le frontend est construit avec React et TypeScript, suivant une architecture modulaire et orientée composants. Voici la décomposition de cette architecture:

#### 1. Structure de Base
- **App (App.tsx)**: Point d'entrée principal de l'application
- **Main (main.tsx)**: Initialisation de l'application React et rendu dans le DOM

#### 2. Composants Réutilisables
Ces composants forment la bibliothèque UI de l'application:
- **Composants Communs**: Button, InputField, Alert, SelectField - éléments UI de base réutilisables
- **Composants de Layout**: Header, Sidebar, MainLayout - gèrent la structure visuelle de l'application
- **Composants de Données**: DataTable, Pagination - pour l'affichage des listes et tableaux de données
- **Composants Métier**: AppointmentCard - composants spécifiques au domaine métier
- **Composant de Chargement**: LoadingScreen - feedback utilisateur pendant les opérations asynchrones

#### 3. Routage
Gère la navigation et les protections d'accès:
- **Routes (routes.tsx)**: Définition de toutes les routes de l'application
- **Navigation**: Hooks et composants (useNavigate, Link) pour la navigation
- **Guards de Route**: RequireAuth et RequireGuest - protections d'accès aux pages

#### 4. Services API
Encapsule la communication avec le backend:
- **API Client (apiClient.ts)**: Client HTTP avec intercepteurs pour la gestion des tokens
- **Endpoints (endpoints.ts)**: Points d'entrée API centralisés
- **Services Spécifiques**: authService, patientService, appointmentService - abstraction des appels API pour chaque domaine

#### 5. Contextes
État global de l'application:
- **AuthContext**: Gestion de l'authentification et des informations utilisateur au niveau global

#### 6. Pages
Composants de plus haut niveau représentant des écrans complets:
- **Pages Auth**: LoginPage, ForgotPasswordPage
- **Dashboard**: Vue d'ensemble des informations
- **Pages Patient**: Liste, détails, création et modification de patients
- **Pages Rendez-vous**: Calendrier, détails et création de rendez-vous
- **Pages Dossiers Médicaux**: Visualisation et téléchargement de documents
- **Page Paramètres**: Configuration utilisateur
- **Page 404**: Gestion des routes inconnues

#### 7. Types
Interfaces TypeScript pour la vérification de type:
- **Types Patient**: Définitions des interfaces pour les patients

### Caractéristiques Architecturales

Cette architecture présente plusieurs avantages:

1. **Séparation des Préoccupations**: Chaque partie du code a une responsabilité claire
2. **Réutilisation**: Les composants UI communs sont partagés dans toute l'application
3. **Modularité**: Organisation en modules fonctionnels facilement maintenables
4. **Gestion d'État**: Utilisation de contextes React pour l'état global
5. **Consistance UI**: Composants standardisés pour une expérience utilisateur cohérente
6. **Protection des Routes**: Sécurisation de l'accès aux différentes parties de l'application
7. **Services Abstraits**: La logique API est encapsulée dans des services dédiés