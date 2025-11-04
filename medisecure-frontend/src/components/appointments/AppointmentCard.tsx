// src/components/appointments/AppointmentCard/AppointmentCard.tsx
import React from "react";
import { Link } from "react-router-dom";

// Définir le type d'état possible pour un rendez-vous
export type AppointmentStatus =
  | "SCHEDULED"
  | "CONFIRMED"
  | "CANCELLED"
  | "COMPLETED";

export interface AppointmentCardProps {
  id: string;
  patientId: string;
  patientName: string;
  doctorName: string;
  startTime: string;
  endTime: string;
  status: AppointmentStatus;
  notes?: string;
  onStatusChange?: (id: string, status: AppointmentStatus) => void;
  className?: string;
}

const AppointmentCard: React.FC<AppointmentCardProps> = ({
  id,
  patientId,
  patientName,
  doctorName,
  startTime,
  endTime,
  status,
  notes,
  onStatusChange,
  className = "",
}) => {
  // Formatage de la date et de l'heure
  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return {
      date: date.toLocaleDateString("fr-FR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      }),
      time: date.toLocaleTimeString("fr-FR", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
  };

  const start = formatDateTime(startTime);
  const end = formatDateTime(endTime);

  // Statut avec classe de couleur et libellé
  const getStatusInfo = (status: AppointmentStatus) => {
    switch (status) {
      case "SCHEDULED":
        return {
          label: "Planifié",
          bgColor: "bg-yellow-100",
          textColor: "text-yellow-800",
        };
      case "CONFIRMED":
        return {
          label: "Confirmé",
          bgColor: "bg-green-100",
          textColor: "text-green-800",
        };
      case "CANCELLED":
        return {
          label: "Annulé",
          bgColor: "bg-red-100",
          textColor: "text-red-800",
        };
      case "COMPLETED":
        return {
          label: "Terminé",
          bgColor: "bg-slate-100",
          textColor: "text-slate-800",
        };
      default:
        return {
          label: "Inconnu",
          bgColor: "bg-slate-100",
          textColor: "text-slate-800",
        };
    }
  };

  const statusInfo = getStatusInfo(status);

  return (
    <div
      className={`p-4 border rounded-lg bg-white shadow-sm hover:shadow-md transition-shadow ${className}`}
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-lg font-medium text-slate-900">
            {start.date} - {start.time}
          </h3>
          <p className="text-sm text-slate-500">{doctorName}</p>
        </div>
        <span
          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusInfo.bgColor} ${statusInfo.textColor}`}
        >
          {statusInfo.label}
        </span>
      </div>

      <div className="mb-3">
        <div className="flex items-center mb-1">
          <svg
            className="h-5 w-5 text-slate-500 mr-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
            />
          </svg>
          <span className="text-slate-900 font-medium">{patientName}</span>
        </div>

        <div className="flex items-center mb-1">
          <svg
            className="h-5 w-5 text-slate-500 mr-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span className="text-slate-700">
            {start.time} - {end.time}
          </span>
        </div>

        {notes && (
          <div className="mt-2 text-sm text-slate-600 border-t pt-2">
            <p>{notes}</p>
          </div>
        )}
      </div>

      <div className="flex justify-between mt-4 pt-3 border-t border-slate-100">
        <div className="flex space-x-2">
          <Link
            to={`/patients/${patientId}`}
            className="text-sm text-primary-600 hover:text-primary-800"
          >
            Fiche patient
          </Link>
          <Link
            to={`/appointments/${id}`}
            className="text-sm text-primary-600 hover:text-primary-800"
          >
            Détails
          </Link>
        </div>

        {onStatusChange &&
          (status === "SCHEDULED" || status === "CONFIRMED") && (
            <div className="flex space-x-2">
              {status === "SCHEDULED" && (
                <button
                  onClick={() => onStatusChange(id, "CONFIRMED")}
                  className="text-sm text-green-600 hover:text-green-800"
                >
                  Confirmer
                </button>
              )}
              <button
                onClick={() => onStatusChange(id, "CANCELLED")}
                className="text-sm text-red-600 hover:text-red-800"
              >
                Annuler
              </button>
              <button
                onClick={() => onStatusChange(id, "COMPLETED")}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Terminer
              </button>
            </div>
          )}
      </div>
    </div>
  );
};

export default AppointmentCard;
