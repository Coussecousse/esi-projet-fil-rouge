// src/pages/appointments/AppointmentDetailsPage.tsx
import React, { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import toast from "react-hot-toast";
import appointmentService, {
  Appointment,
} from "../../api/services/appointmentService";
import patientService from "../../api/services/patientService";
import Button from "../../components/common/Button/Button";
import Alert from "../../components/common/Alert/Alert";
import LoadingScreen from "../../components/common/LoadingScreen/LoadingScreen";

const AppointmentDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [appointment, setAppointment] = useState<Appointment | null>(null);
  const [patientName, setPatientName] = useState<string>("Chargement...");
  const [doctorName, setDoctorName] = useState<string>("Chargement...");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // Fonction pour charger les détails du rendez-vous
  const fetchAppointmentDetails = useCallback(async () => {
    if (!id) return;

    try {
      setLoading(true);
      setError(null);

      // Récupérer les données du rendez-vous
      const appointmentData = await appointmentService.getAppointmentById(id);

      if (!appointmentData) {
        setError("Ce rendez-vous n'existe pas ou a été supprimé");
        setLoading(false);
        return;
      }

      setAppointment(appointmentData);

      // Essayer de récupérer les détails du patient
      try {
        const patientData = await patientService.getPatientById(
          appointmentData.patientId
        );
        if (patientData) {
          setPatientName(`${patientData.firstName} ${patientData.lastName}`);
        } else {
          setPatientName(`Patient (ID: ${appointmentData.patientId})`);
        }
      } catch (error) {
        console.error("Erreur lors de la récupération du patient:", error);
        setPatientName(`Patient (ID: ${appointmentData.patientId})`);
      }

      // En pratique, il faudrait aussi récupérer les informations du médecin
      setDoctorName(`Médecin (ID: ${appointmentData.doctorId})`);
    } catch (error) {
      console.error("Erreur lors du chargement du rendez-vous:", error);
      setError("Erreur lors du chargement des détails du rendez-vous");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchAppointmentDetails();
  }, [fetchAppointmentDetails]);

  const handleStatusChange = async (newStatus: Appointment["status"]) => {
    if (!id || !appointment) return;

    try {
      setIsProcessing(true);
      setError(null);

      let updatedAppointment = null;

      if (newStatus === "CANCELLED") {
        updatedAppointment = await appointmentService.cancelAppointment(id);
      } else if (newStatus === "CONFIRMED") {
        updatedAppointment = await appointmentService.confirmAppointment(id);
      } else if (newStatus === "COMPLETED") {
        updatedAppointment = await appointmentService.completeAppointment(id);
      }

      if (updatedAppointment) {
        setAppointment(updatedAppointment);

        const statusMessages = {
          CONFIRMED: "Rendez-vous confirmé avec succès",
          CANCELLED: "Rendez-vous annulé avec succès",
          COMPLETED: "Rendez-vous marqué comme terminé",
          SCHEDULED: "Rendez-vous reprogrammé avec succès",
        };

        toast.success(statusMessages[newStatus]);
      } else {
        toast.error("Erreur lors de la mise à jour du statut");
      }
    } catch (error) {
      console.error(
        `Erreur lors de la mise à jour du statut vers ${newStatus}:`,
        error
      );
      setError(`Erreur lors de la mise à jour du statut du rendez-vous`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Formatage de la date et de l'heure
  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return {
      date: date.toLocaleDateString("fr-FR", {
        weekday: "long",
        day: "numeric",
        month: "long",
        year: "numeric",
      }),
      time: date.toLocaleTimeString("fr-FR", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
  };

  if (loading) {
    return <LoadingScreen />;
  }

  if (!appointment) {
    return (
      <div className="text-center py-10">
        <h2 className="text-2xl font-semibold text-slate-900 mb-2">
          Rendez-vous non trouvé
        </h2>
        <p className="text-slate-600 mb-6">
          Le rendez-vous que vous recherchez n'existe pas ou a été supprimé.
        </p>
        <Button variant="primary" onClick={() => navigate("/appointments")}>
          Retour à la liste des rendez-vous
        </Button>
      </div>
    );
  }

  const startDateTime = formatDateTime(appointment.startTime);
  const endDateTime = formatDateTime(appointment.endTime);

  // Obtenir la classe de couleur en fonction du statut
  const getStatusClass = (status: Appointment["status"]) => {
    switch (status) {
      case "CONFIRMED":
        return "bg-green-100 text-green-800";
      case "SCHEDULED":
        return "bg-yellow-100 text-yellow-800";
      case "CANCELLED":
        return "bg-red-100 text-red-800";
      case "COMPLETED":
        return "bg-slate-100 text-slate-800";
      default:
        return "bg-slate-100 text-slate-800";
    }
  };

  // Obtenir le libellé du statut
  const getStatusLabel = (status: Appointment["status"]) => {
    switch (status) {
      case "CONFIRMED":
        return "Confirmé";
      case "SCHEDULED":
        return "Planifié";
      case "CANCELLED":
        return "Annulé";
      case "COMPLETED":
        return "Terminé";
      default:
        return "Inconnu";
    }
  };

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">
            Détails du rendez-vous
          </h1>
          <p className="text-slate-500">
            {startDateTime.date} • {startDateTime.time} - {endDateTime.time}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" onClick={() => navigate(-1)}>
            Retour
          </Button>
          <Button variant="primary" onClick={fetchAppointmentDetails}>
            Actualiser
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="error" message={error} onClose={() => setError(null)} />
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Informations principales */}
        <div className="card lg:col-span-2">
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-lg font-medium text-slate-900">
              Informations du rendez-vous
            </h2>
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusClass(
                appointment.status
              )}`}
            >
              {getStatusLabel(appointment.status)}
            </span>
          </div>

          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-medium text-slate-500">Patient</h3>
                <p className="mt-1 text-slate-900">{patientName}</p>
                <Link
                  to={`/patients/${appointment.patientId}`}
                  className="text-sm text-primary-600 hover:text-primary-800"
                >
                  Voir la fiche patient
                </Link>
              </div>

              <div>
                <h3 className="text-sm font-medium text-slate-500">Médecin</h3>
                <p className="mt-1 text-slate-900">{doctorName}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-medium text-slate-500">Date</h3>
                <p className="mt-1 text-slate-900">{startDateTime.date}</p>
              </div>

              <div>
                <h3 className="text-sm font-medium text-slate-500">Horaire</h3>
                <p className="mt-1 text-slate-900">
                  {startDateTime.time} - {endDateTime.time}
                </p>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium text-slate-500">
                Motif du rendez-vous
              </h3>
              <p className="mt-1 text-slate-900">
                {appointment.reason || "Non spécifié"}
              </p>
            </div>

            <div>
              <h3 className="text-sm font-medium text-slate-500">Notes</h3>
              <div className="mt-1 text-slate-900 whitespace-pre-line">
                {appointment.notes || "Aucune note"}
              </div>
            </div>
          </div>
        </div>

        {/* Actions et historique */}
        <div className="card">
          <h2 className="text-lg font-medium text-slate-900 mb-4">Actions</h2>

          <div className="space-y-4">
            {appointment.status === "SCHEDULED" && (
              <Button
                variant="primary"
                fullWidth
                onClick={() => handleStatusChange("CONFIRMED")}
                isLoading={isProcessing}
                disabled={isProcessing}
              >
                Confirmer le rendez-vous
              </Button>
            )}

            {appointment.status === "SCHEDULED" ||
            appointment.status === "CONFIRMED" ? (
              <>
                <Button
                  variant="success"
                  fullWidth
                  onClick={() => handleStatusChange("COMPLETED")}
                  isLoading={isProcessing}
                  disabled={isProcessing}
                >
                  Marquer comme effectué
                </Button>

                <Button
                  variant="danger"
                  fullWidth
                  onClick={() => handleStatusChange("CANCELLED")}
                  isLoading={isProcessing}
                  disabled={isProcessing}
                >
                  Annuler le rendez-vous
                </Button>
              </>
            ) : null}

            <Link
              to={`/appointments/create?patientId=${appointment.patientId}`}
              className="block mt-4"
            >
              <Button variant="outline" fullWidth>
                Planifier un nouveau rendez-vous
              </Button>
            </Link>
          </div>

          <div className="mt-6 pt-6 border-t border-slate-200">
            <h3 className="text-sm font-medium text-slate-500 mb-3">
              Historique
            </h3>

            <div className="space-y-3">
              <div className="flex items-start">
                <div className="flex-shrink-0 h-5 w-5 rounded-full bg-green-100 flex items-center justify-center">
                  <span className="h-3 w-3 rounded-full bg-green-600"></span>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-slate-900">
                    Rendez-vous créé
                  </p>
                  <p className="text-xs text-slate-500">
                    {new Date(appointment.createdAt).toLocaleDateString(
                      "fr-FR",
                      {
                        day: "numeric",
                        month: "long",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      }
                    )}
                  </p>
                </div>
              </div>

              {appointment.updatedAt !== appointment.createdAt && (
                <div className="flex items-start">
                  <div className="flex-shrink-0 h-5 w-5 rounded-full bg-blue-100 flex items-center justify-center">
                    <span className="h-3 w-3 rounded-full bg-blue-600"></span>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-slate-900">
                      Rendez-vous mis à jour
                    </p>
                    <p className="text-xs text-slate-500">
                      {new Date(appointment.updatedAt).toLocaleDateString(
                        "fr-FR",
                        {
                          day: "numeric",
                          month: "long",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        }
                      )}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AppointmentDetailsPage;
