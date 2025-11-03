// src/pages/appointments/AppointmentsCalendarPage.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import appointmentService, { Appointment } from "../../api/services/appointmentService";
import Button from "../../components/common/Button/Button";
import LoadingScreen from "../../components/common/LoadingScreen/LoadingScreen";
import Alert from "../../components/common/Alert/Alert";

// Types pour les jours du calendrier
interface CalendarDay {
  date: Date;
  isCurrentMonth: boolean;
  isToday: boolean;
  appointments: Appointment[];
}

const AppointmentsCalendarPage: React.FC = () => {
  const navigate = useNavigate();
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [calendarDays, setCalendarDays] = useState<CalendarDay[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDay, setSelectedDay] = useState<Date | null>(null);
  const [dayAppointments, setDayAppointments] = useState<Appointment[]>([]);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Fonction pour déclencher un rafraîchissement des données
  const refreshData = useCallback(() => {
    setRefreshTrigger((prev) => prev + 1);
  }, []);

  // Charger les rendez-vous
  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        setLoading(true);
        setError(null);

        const year = currentMonth.getFullYear();
        const month = currentMonth.getMonth() + 1; // JavaScript months are 0-based

        console.log(`Fetching appointments for ${year}/${month}`);
        const fetchedAppointments =
          await appointmentService.getAppointmentsCalendar(year, month);

        console.log("Fetched appointments:", fetchedAppointments);
        setAppointments(fetchedAppointments);
      } catch (error) {
        console.error("Error fetching appointments:", error);
        setError("Erreur lors du chargement des rendez-vous");
      } finally {
        setLoading(false);
      }
    };

    fetchAppointments();
  }, [currentMonth, refreshTrigger]);

  // Générer les jours du calendrier
  useEffect(() => {
    const generateCalendarDays = () => {
      const year = currentMonth.getFullYear();
      const month = currentMonth.getMonth();

      // Premier jour du mois
      const firstDayOfMonth = new Date(year, month, 1);
      // Dernier jour du mois
      const lastDayOfMonth = new Date(year, month + 1, 0);

      // Jour de la semaine du premier jour (0: dimanche, 1: lundi, ..., 6: samedi)
      const firstDayOfWeek = firstDayOfMonth.getDay();

      // Calculer le premier jour à afficher (peut être du mois précédent)
      const start = new Date(firstDayOfMonth);
      // Ajuster pour commencer le lundi (0 = dimanche, 1 = lundi, etc.)
      start.setDate(
        start.getDate() - (firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1)
      );

      const days: CalendarDay[] = [];
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      // Générer 42 jours (6 semaines)
      for (let i = 0; i < 42; i++) {
        const date = new Date(start);
        date.setDate(date.getDate() + i);

        const isCurrentMonth = date.getMonth() === month;
        const isToday = date.toDateString() === today.toDateString();

        // Filtrer les rendez-vous pour cette journée
        const dayAppts = appointments.filter((appointment) => {
          const apptDate = new Date(appointment.startTime);
          return (
            apptDate.getFullYear() === date.getFullYear() &&
            apptDate.getMonth() === date.getMonth() &&
            apptDate.getDate() === date.getDate()
          );
        });

        days.push({
          date,
          isCurrentMonth,
          isToday,
          appointments: dayAppts,
        });
      }

      setCalendarDays(days);
    };

    if (appointments.length > 0 || calendarDays.length === 0) {
      generateCalendarDays();
    }
  }, [currentMonth, appointments]);

  // Mettre à jour les rendez-vous du jour sélectionné
  useEffect(() => {
    if (!selectedDay) {
      setDayAppointments([]);
      return;
    }

    const filteredAppointments = appointments.filter((appointment) => {
      const apptDate = new Date(appointment.startTime);
      return (
        apptDate.getFullYear() === selectedDay.getFullYear() &&
        apptDate.getMonth() === selectedDay.getMonth() &&
        apptDate.getDate() === selectedDay.getDate()
      );
    });

    // Trier par heure de début
    filteredAppointments.sort(
      (a, b) =>
        new Date(a.startTime).getTime() - new Date(b.startTime).getTime()
    );

    setDayAppointments(filteredAppointments);
  }, [selectedDay, appointments]);

  // Naviguer au mois précédent
  const goToPreviousMonth = () => {
    setCurrentMonth((prev) => {
      const newMonth = new Date(prev);
      newMonth.setMonth(prev.getMonth() - 1);
      return newMonth;
    });
  };

  // Naviguer au mois suivant
  const goToNextMonth = () => {
    setCurrentMonth((prev) => {
      const newMonth = new Date(prev);
      newMonth.setMonth(prev.getMonth() + 1);
      return newMonth;
    });
  };

  // Naviguer au mois courant
  const goToCurrentMonth = () => {
    const now = new Date();
    setCurrentMonth(new Date(now.getFullYear(), now.getMonth(), 1));
    setSelectedDay(new Date(now.getFullYear(), now.getMonth(), now.getDate()));
  };

  // Formater l'heure
  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString("fr-FR", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Gérer la sélection d'un jour
  const handleDayClick = (day: CalendarDay) => {
    setSelectedDay(day.date);
  };

  // Gérer le changement de statut d'un rendez-vous
  const handleStatusChange = async (
    id: string,
    newStatus: Appointment["status"]
  ) => {
    try {
      let result = null;

      if (newStatus === "CANCELLED") {
        result = await appointmentService.cancelAppointment(id);
      } else if (newStatus === "CONFIRMED") {
        result = await appointmentService.confirmAppointment(id);
      } else if (newStatus === "COMPLETED") {
        result = await appointmentService.completeAppointment(id);
      }

      if (result) {
        // Mettre à jour localement
        setAppointments((prev) =>
          prev.map((apt) =>
            apt.id === id ? { ...apt, status: newStatus } : apt
          )
        );

        // Mettre à jour les rendez-vous du jour
        if (selectedDay) {
          setDayAppointments((prev) =>
            prev.map((apt) =>
              apt.id === id ? { ...apt, status: newStatus } : apt
            )
          );
        }

        // Message de succès
        const messages = {
          CONFIRMED: "Rendez-vous confirmé",
          CANCELLED: "Rendez-vous annulé",
          COMPLETED: "Rendez-vous marqué comme terminé",
          SCHEDULED: "Rendez-vous replanifié",
        };

        toast.success(messages[newStatus]);
      } else {
        toast.error("Erreur lors de la mise à jour du rendez-vous");
      }
    } catch (error) {
      console.error(
        `Erreur lors de la mise à jour du statut vers ${newStatus}:`,
        error
      );
      toast.error("Erreur lors de la mise à jour du statut");
    }
  };

  // Obtenir le statut d'un rendez-vous sous forme de badge
  const getStatusBadge = (status: Appointment["status"]) => {
    switch (status) {
      case "CONFIRMED":
        return <span className="badge badge-success">Confirmé</span>;
      case "SCHEDULED":
        return <span className="badge badge-warning">Planifié</span>;
      case "CANCELLED":
        return <span className="badge badge-error">Annulé</span>;
      case "COMPLETED":
        return (
          <span className="badge bg-slate-100 text-slate-800">Terminé</span>
        );
      default:
        return null;
    }
  };

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-center space-y-4 md:space-y-0">
        <h1 className="text-2xl font-semibold text-slate-900">
          Calendrier des rendez-vous
        </h1>
        <div className="flex space-x-2">
          <Link
            to="/appointments/create"
            className="btn btn-primary inline-flex items-center"
          >
            <svg
              className="h-5 w-5 mr-2"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 6v6m0 0v6m0-6h6m-6 0H6"
              />
            </svg>
            Nouveau rendez-vous
          </Link>
          <Button variant="outline" onClick={refreshData}>
            <svg
              className="h-5 w-5 mr-2"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
            Actualiser
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="error" message={error} onClose={() => setError(null)} />
      )}

      {/* Calendrier */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendrier mensuel */}
        <div className="lg:col-span-2">
          <div className="card">
            {/* Navigation du calendrier */}
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-slate-900">
                {currentMonth.toLocaleDateString("fr-FR", {
                  month: "long",
                  year: "numeric",
                })}
              </h2>
              <div className="flex space-x-2">
                <button
                  onClick={goToPreviousMonth}
                  className="p-2 text-slate-600 hover:text-primary-600 focus:outline-none"
                >
                  <svg
                    className="h-5 w-5"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 19l-7-7 7-7"
                    />
                  </svg>
                </button>
                <button
                  onClick={goToCurrentMonth}
                  className="p-2 text-slate-600 hover:text-primary-600 focus:outline-none"
                >
                  Aujourd'hui
                </button>
                <button
                  onClick={goToNextMonth}
                  className="p-2 text-slate-600 hover:text-primary-600 focus:outline-none"
                >
                  <svg
                    className="h-5 w-5"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </button>
              </div>
            </div>

            {/* Grille des jours de la semaine */}
            <div className="grid grid-cols-7 gap-px bg-slate-200">
              {["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"].map((day) => (
                <div
                  key={day}
                  className="bg-slate-100 text-center py-2 text-sm font-medium text-slate-600"
                >
                  {day}
                </div>
              ))}
            </div>

            {/* Grille des jours */}
            <div className="grid grid-cols-7 gap-px bg-slate-200">
              {calendarDays.map((day, index) => (
                <div
                  key={index}
                  className={`bg-white min-h-[100px] p-2 ${
                    !day.isCurrentMonth ? "opacity-50" : ""
                  } ${day.isToday ? "bg-primary-50" : ""} ${
                    selectedDay &&
                    selectedDay.getFullYear() === day.date.getFullYear() &&
                    selectedDay.getMonth() === day.date.getMonth() &&
                    selectedDay.getDate() === day.date.getDate()
                      ? "ring-2 ring-primary-500 ring-inset"
                      : ""
                  } hover:bg-slate-50 cursor-pointer transition`}
                  onClick={() => handleDayClick(day)}
                >
                  <div className="flex flex-col h-full">
                    <div
                      className={`text-sm font-medium ${
                        day.isToday ? "text-primary-600" : "text-slate-900"
                      }`}
                    >
                      {day.date.getDate()}
                    </div>
                    <div className="flex-1 overflow-y-auto mt-1 space-y-1">
                      {day.appointments.slice(0, 3).map((appointment) => (
                        <div
                          key={appointment.id}
                          className={`text-xs p-1 rounded truncate ${
                            appointment.status === "CONFIRMED"
                              ? "bg-green-100 text-green-800"
                              : appointment.status === "SCHEDULED"
                              ? "bg-yellow-100 text-yellow-800"
                              : appointment.status === "CANCELLED"
                              ? "bg-red-100 text-red-800"
                              : "bg-slate-100 text-slate-800"
                          }`}
                        >
                          {formatTime(appointment.startTime)} -
                          {appointment.patientId
                            ? "ID: " + appointment.patientId.substring(0, 8)
                            : "Patient"}
                        </div>
                      ))}
                      {day.appointments.length > 3 && (
                        <div className="text-xs text-slate-500 p-1">
                          +{day.appointments.length - 3} autre(s)
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Détails du jour sélectionné */}
        <div className="card">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">
            {selectedDay
              ? selectedDay.toLocaleDateString("fr-FR", {
                  weekday: "long",
                  day: "numeric",
                  month: "long",
                  year: "numeric",
                })
              : "Sélectionnez une date"}
          </h2>

          {selectedDay && dayAppointments.length === 0 ? (
            <div className="text-center py-6 text-slate-500">
              <svg
                className="mx-auto h-12 w-12 text-slate-400"
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
              <p className="mt-2">Aucun rendez-vous pour cette date</p>
              <div className="mt-4">
                <Link
                  to={`/appointments/create?date=${
                    selectedDay.toISOString().split("T")[0]
                  }`}
                  className="btn btn-primary"
                >
                  Ajouter un rendez-vous
                </Link>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {dayAppointments.map((appointment) => (
                <div
                  key={appointment.id}
                  className="p-3 border border-slate-100 rounded-lg hover:bg-slate-50"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="text-sm font-medium text-slate-900">
                      {formatTime(appointment.startTime)} -{" "}
                      {formatTime(appointment.endTime)}
                    </div>
                    {getStatusBadge(appointment.status)}
                  </div>
                  <div className="text-slate-900 font-medium mb-1">
                    Patient ID: {appointment.patientId}
                  </div>
                  <div className="text-slate-900 font-medium mb-1">
                    Médecin ID: {appointment.doctorId}
                  </div>
                  {appointment.notes && (
                    <div className="text-sm text-slate-600 mb-2">
                      {appointment.notes}
                    </div>
                  )}
                  <div className="flex mt-2 space-x-3">
                    <Link
                      to={`/appointments/${appointment.id}`}
                      className="text-sm text-primary-600 hover:text-primary-700"
                    >
                      Détails
                    </Link>
                    <Link
                      to={`/patients/${appointment.patientId}`}
                      className="text-sm text-secondary-600 hover:text-secondary-700"
                    >
                      Voir patient
                    </Link>

                    {/* Actions de changement de statut */}
                    {appointment.status === "SCHEDULED" && (
                      <button
                        onClick={() =>
                          handleStatusChange(appointment.id, "CONFIRMED")
                        }
                        className="text-sm text-green-600 hover:text-green-700"
                      >
                        Confirmer
                      </button>
                    )}

                    {(appointment.status === "SCHEDULED" ||
                      appointment.status === "CONFIRMED") && (
                      <>
                        <button
                          onClick={() =>
                            handleStatusChange(appointment.id, "COMPLETED")
                          }
                          className="text-sm text-blue-600 hover:text-blue-700"
                        >
                          Terminer
                        </button>
                        <button
                          onClick={() =>
                            handleStatusChange(appointment.id, "CANCELLED")
                          }
                          className="text-sm text-red-600 hover:text-red-700"
                        >
                          Annuler
                        </button>
                      </>
                    )}
                  </div>
                </div>
              ))}
              {selectedDay && (
                <div className="pt-4 border-t border-slate-100">
                  <Link
                    to={`/appointments/create?date=${
                      selectedDay.toISOString().split("T")[0]
                    }`}
                    className="btn btn-primary w-full"
                  >
                    Ajouter un rendez-vous
                  </Link>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AppointmentsCalendarPage;