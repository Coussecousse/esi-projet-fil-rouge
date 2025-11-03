// src/routes.tsx - Mise à jour avec les nouvelles routes
import { JSX, lazy, Suspense } from "react";
import { Navigate, useRoutes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";

// Layouts
import MainLayout from "./components/layout/MainLayout/MainLayout";

// Components
import LoadingScreen from "./components/common/LoadingScreen/LoadingScreen";

// Lazy-loaded pages
const SettingsPage = lazy(() => import("./pages/settings/SettingsPage"));
const MedicalRecordsPage = lazy(
  () => import("./pages/medical-records/MedicalRecordsPage")
);
const UploadDocumentPage = lazy(
  () => import("./pages/medical-records/UploadDocumentPage")
);
const Dashboard = lazy(() => import("./pages/dashboard/DashBoardPage"));
const LoginPage = lazy(() => import("./pages/auth/LoginPage"));
const ForgotPasswordPage = lazy(
  () => import("./pages/auth/ForgotPasswordPage")
);

// Patients
const PatientListPage = lazy(() => import("./pages/patients/PatientsListPage"));
const PatientDetailsPage = lazy(
  () => import("./pages/patients/PatientDetailsPage")
);
const CreatePatientPage = lazy(
  () => import("./pages/patients/CreatePatientPage")
);
const EditPatientPage = lazy(() => import("./pages/patients/EditPatientPage"));

// Appointments
const AppointmentsCalendarPage = lazy(
  () => import("./pages/appointments/AppointmentsCalendarPage")
);
const AppointmentDetailsPage = lazy(
  () => import("./pages/appointments/AppointmentDetailsPage")
);
const CreateAppointmentPage = lazy(
  () => import("./pages/appointments/CreateAppointmentPage")
);

// Settings & Others
const NotFoundPage = lazy(() => import("./pages/NotFoundPage"));

const RouteProgress = ({ children }: { children: React.ReactNode }) => {
  return <Suspense fallback={<LoadingScreen />}>{children}</Suspense>;
};

// Guard pour les routes protégées
const RequireAuth = ({ children }: { children: JSX.Element }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Guard pour les routes publiques (uniquement accessibles lorsque non connecté)
const RequireGuest = ({ children }: { children: JSX.Element }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

const AppRoutes = () => {
  return useRoutes([
    // Routes publiques
    {
      path: "/login",
      element: (
        <RequireGuest>
          <RouteProgress>
            <LoginPage />
          </RouteProgress>
        </RequireGuest>
      ),
    },
    {
      path: "/forgot-password",
      element: (
        <RequireGuest>
          <RouteProgress>
            <ForgotPasswordPage />
          </RouteProgress>
        </RequireGuest>
      ),
    },

    // Routes protégées
    {
      path: "/",
      element: (
        <RequireAuth>
          <MainLayout />
        </RequireAuth>
      ),
      children: [
        { path: "/", element: <Navigate to="/dashboard" replace /> },
        {
          path: "dashboard",
          element: (
            <RouteProgress>
              <Dashboard />
            </RouteProgress>
          ),
        },
        // Routes Patients
        {
          path: "patients",
          element: (
            <RouteProgress>
              <PatientListPage />
            </RouteProgress>
          ),
        },
        {
          path: "patients/create",
          element: (
            <RouteProgress>
              <CreatePatientPage />
            </RouteProgress>
          ),
        },
        {
          path: "patients/:id",
          element: (
            <RouteProgress>
              <PatientDetailsPage />
            </RouteProgress>
          ),
        },
        {
          path: "patients/:id/edit",
          element: (
            <RouteProgress>
              <EditPatientPage />
            </RouteProgress>
          ),
        },
        // Routes Rendez-vous
        {
          path: "appointments",
          element: (
            <RouteProgress>
              <AppointmentsCalendarPage />
            </RouteProgress>
          ),
        },
        {
          path: "appointments/create",
          element: (
            <RouteProgress>
              <CreateAppointmentPage />
            </RouteProgress>
          ),
        },
        {
          path: "appointments/:id",
          element: (
            <RouteProgress>
              <AppointmentDetailsPage />
            </RouteProgress>
          ),
        },
        {
          path: "settings",
          element: (
            <RouteProgress>
              <SettingsPage />
            </RouteProgress>
          ),
        },
        {
          path: "medical-records",
          element: (
            <RouteProgress>
              <MedicalRecordsPage />
            </RouteProgress>
          ),
        },
        {
          path: "medical-records/:recordId",
          element: (
            <RouteProgress>
              <MedicalRecordsPage />
            </RouteProgress>
          ),
        },
        {
          path: "medical-records/upload",
          element: (
            <RouteProgress>
              <UploadDocumentPage />
            </RouteProgress>
          ),
        },
        {
          path: "medical-records/:recordId/upload",
          element: (
            <RouteProgress>
              <UploadDocumentPage />
            </RouteProgress>
          ),
        },
      ],
    },

    // Route 404
    {
      path: "*",
      element: (
        <RouteProgress>
          <NotFoundPage />
        </RouteProgress>
      ),
    },
  ]);
};

export default AppRoutes;
