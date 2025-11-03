// src/pages/dashboard/DashboardPage.tsx
import React, { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import patientService from "../../api/services/patientService";
import appointmentService from "../../api/services/appointmentService";
import { Patient } from "../../types/patient.types";
import { Appointment } from "../../api/services/appointmentService";
import LoadingScreen from "../../components/common/LoadingScreen/LoadingScreen";
import Alert from "../../components/common/Alert/Alert";

// Types pour les statistiques
interface DashboardStats {
  totalPatients: number;
  totalAppointmentsToday: number;
  upcomingAppointments: number;
  pendingMedicalRecords: number;
}

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalPatients: 0,
    totalAppointmentsToday: 0,
    upcomingAppointments: 0,
    pendingMedicalRecords: 0,
  });
  const [recentPatients, setRecentPatients] = useState<Patient[]>([]);
  const [upcomingAppointments, setUpcomingAppointments] = useState<
    Appointment[]
  >([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fonction pour charger les données du tableau de bord
  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Récupérer les patients
      const patients = await patientService.getAllPatients();
      setRecentPatients(patients.slice(0, 5)); // Les 5 plus récents

      // Récupérer les rendez-vous
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      const todayStr = today.toISOString().split("T")[0];

      // Calcul de la date dans 7 jours
      const nextWeek = new Date(today);
      nextWeek.setDate(nextWeek.getDate() + 7);
      const nextWeekStr = nextWeek.toISOString().split("T")[0];

      // Filtre pour aujourd'hui et la semaine à venir
      const filter = {
        startDate: todayStr,
        endDate: nextWeekStr,
      };

      const appointments = await appointmentService.getAllAppointments(filter);

      // Filtrer les rendez-vous d'aujourd'hui
      const todayAppointments = appointments.filter((appointment) => {
        const appointmentDate = new Date(appointment.startTime);
        return appointmentDate.toDateString() === today.toDateString();
      });

      // Prendre les 4 prochains rendez-vous à venir pour l'affichage
      const upcoming = appointments
        .filter((appointment) => new Date(appointment.startTime) >= today)
        .sort(
          (a, b) =>
            new Date(a.startTime).getTime() - new Date(b.startTime).getTime()
        )
        .slice(0, 4);

      setUpcomingAppointments(upcoming);

      // Mettre à jour les statistiques
      setStats({
        totalPatients: patients.length,
        totalAppointmentsToday: todayAppointments.length,
        upcomingAppointments: appointments.filter(
          (apt) =>
            new Date(apt.startTime) >= today &&
            new Date(apt.startTime) <= nextWeek
        ).length,
        pendingMedicalRecords: 0, // Cette fonctionnalité n'est pas encore implémentée
      });
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      setError("Erreur lors du chargement des données du tableau de bord");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Formatage de la date pour affichage
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("fr-FR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  };

  // Calculer l'âge à partir de la date de naissance
  const calculateAge = (dateOfBirth: string): number => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();

    if (
      monthDiff < 0 ||
      (monthDiff === 0 && today.getDate() < birthDate.getDate())
    ) {
      age--;
    }

    return age;
  };

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-slate-900">
          Tableau de bord
        </h1>
        <div className="text-sm text-slate-500">
          {new Date().toLocaleDateString("fr-FR", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </div>
      </div>

      {error && (
        <Alert variant="error" message={error} onClose={() => setError(null)} />
      )}

      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="text-slate-500 text-sm font-medium mb-2">
            Patients totaux
          </div>
          <div className="flex items-end justify-between">
            <div className="text-3xl font-bold text-slate-900">
              {stats.totalPatients}
            </div>
            <div className="text-success-500 text-sm font-medium">
              {stats.totalPatients > 0 ? "+1 cette semaine" : ""}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="text-slate-500 text-sm font-medium mb-2">
            Rendez-vous aujourd'hui
          </div>
          <div className="flex items-end justify-between">
            <div className="text-3xl font-bold text-slate-900">
              {stats.totalAppointmentsToday}
            </div>
            <div className="text-slate-500 text-sm font-medium">
              {stats.totalAppointmentsToday > 0 ? "À venir aujourd'hui" : ""}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="text-slate-500 text-sm font-medium mb-2">
            Rendez-vous à venir
          </div>
          <div className="flex items-end justify-between">
            <div className="text-3xl font-bold text-slate-900">
              {stats.upcomingAppointments}
            </div>
            <div className="text-slate-500 text-sm font-medium">7 jours</div>
          </div>
        </div>

        <div className="card">
          <div className="text-slate-500 text-sm font-medium mb-2">
            Dossiers en attente
          </div>
          <div className="flex items-end justify-between">
            <div className="text-3xl font-bold text-slate-900">
              {stats.pendingMedicalRecords}
            </div>
            <div className="text-warning-500 text-sm font-medium">
              {stats.pendingMedicalRecords > 0 ? "Action requise" : ""}
            </div>
          </div>
        </div>
      </div>

      {/* Contenu principal */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Patients récents */}
        <div className="card overflow-hidden">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-slate-900">
              Patients récents
            </h2>
            <Link
              to="/patients"
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              Voir tous
            </Link>
          </div>

          {recentPatients.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              <p>Aucun patient enregistré</p>
              <Link
                to="/patients/create"
                className="btn btn-primary mt-4 inline-block"
              >
                Ajouter un patient
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto -mx-6 px-6">
              <table className="min-w-full divide-y divide-neutral-200">
                <thead>
                  <tr>
                    <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Nom
                    </th>
                    <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Date de naissance
                    </th>
                    <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Contact
                    </th>
                    <th className="px-3 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-neutral-200">
                  {recentPatients.map((patient) => (
                    <tr key={patient.id} className="hover:bg-slate-50">
                      <td className="px-3 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700">
                            {patient.firstName.charAt(0) +
                              patient.lastName.charAt(0)}
                          </div>
                          <div className="ml-3">
                            <div className="text-sm font-medium text-slate-900">
                              {patient.firstName} {patient.lastName}
                            </div>
                            <div className="text-xs text-slate-500">
                              {patient.gender === "male" ? "Homme" : "Femme"}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-3 py-4 whitespace-nowrap">
                        <div className="text-sm text-slate-900">
                          {new Date(patient.dateOfBirth).toLocaleDateString(
                            "fr-FR"
                          )}
                        </div>
                        <div className="text-xs text-slate-500">
                          {calculateAge(patient.dateOfBirth)} ans
                        </div>
                      </td>
                      <td className="px-3 py-4 whitespace-nowrap">
                        <div className="text-sm text-slate-900">
                          {patient.email || "Non renseigné"}
                        </div>
                        <div className="text-xs text-slate-500">
                          {patient.phone || "Non renseigné"}
                        </div>
                      </td>
                      <td className="px-3 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <Link
                          to={`/patients/${patient.id}`}
                          className="text-primary-600 hover:text-primary-900 mr-3"
                        >
                          Détails
                        </Link>
                        <Link
                          to={`/appointments/create?patientId=${patient.id}`}
                          className="text-secondary-600 hover:text-secondary-900"
                        >
                          RDV
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Rendez-vous à venir */}
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-slate-900">
              Rendez-vous à venir
            </h2>
            <Link
              to="/appointments"
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              Voir tous
            </Link>
          </div>

          {upcomingAppointments.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              <p>Aucun rendez-vous prévu</p>
              <Link
                to="/appointments/create"
                className="btn btn-primary mt-4 inline-block"
              >
                Planifier un rendez-vous
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {upcomingAppointments.map((appointment) => (
                <div
                  key={appointment.id}
                  className="flex p-3 border border-slate-100 rounded-lg hover:bg-slate-50"
                >
                  <div className="mr-4 flex-shrink-0">
                    <div className="h-12 w-12 rounded-lg bg-primary-50 text-primary-700 flex items-center justify-center">
                      <svg
                        className="h-6 w-6"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                        />
                      </svg>
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-start">
                      <p className="text-sm font-medium text-slate-900 truncate">
                        Patient ID: {appointment.patientId}
                      </p>
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          appointment.status === "CONFIRMED"
                            ? "bg-green-100 text-green-800"
                            : "bg-yellow-100 text-yellow-800"
                        }`}
                      >
                        {appointment.status === "CONFIRMED"
                          ? "Confirmé"
                          : appointment.status === "SCHEDULED"
                          ? "Planifié"
                          : appointment.status === "CANCELLED"
                          ? "Annulé"
                          : "Terminé"}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-slate-500">
                      {formatDate(appointment.startTime)}
                    </p>
                    <div className="mt-2 flex">
                      <Link
                        to={`/appointments/${appointment.id}`}
                        className="text-sm text-primary-600 hover:text-primary-700 mr-4"
                      >
                        Détails
                      </Link>
                      <Link
                        to={`/patients/${appointment.patientId}`}
                        className="text-sm text-secondary-600 hover:text-secondary-700 mr-4"
                      >
                        Voir patient
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Bouton pour rafraîchir les données */}
      <div className="flex justify-center">
        <button className="btn btn-outline" onClick={fetchDashboardData}>
          Rafraîchir les données
        </button>
      </div>
    </div>
  );
};

export default DashboardPage;
