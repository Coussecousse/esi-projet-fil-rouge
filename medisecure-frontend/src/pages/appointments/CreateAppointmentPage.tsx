// src/pages/appointments/CreateAppointmentPage.tsx
import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import toast from "react-hot-toast";
import { Patient } from "../../types/patient.types";
import patientService from "../../api/services/patientService";
import appointmentService, {
  AppointmentCreateDto,
} from "../../api/services/appointmentService";
import InputField from "../../components/common/InputField/InputField";
import SelectField from "../../components/common/SelectField/SelectField";
import Button from "../../components/common/Button/Button";
import Alert from "../../components/common/Alert/Alert";
import LoadingScreen from "../../components/common/LoadingScreen/LoadingScreen";

// Schéma de validation
const appointmentSchema = z.object({
  patientId: z.string().min(1, "Veuillez sélectionner un patient"),
  date: z.string().min(1, "La date est requise"),
  startTime: z.string().min(1, "L'heure de début est requise"),
  endTime: z.string().min(1, "L'heure de fin est requise"),
  doctorId: z.string().min(1, "Veuillez sélectionner un médecin"),
  reason: z.string().optional(),
  notes: z.string().optional(),
  status: z.enum(["SCHEDULED", "CONFIRMED", "CANCELLED", "COMPLETED"]),
});

type FormData = z.infer<typeof appointmentSchema>;

// Interfaces pour les types de données utilisés
interface Doctor {
  id: string;
  first_name: string;
  last_name: string;
  role: string;
  specialty?: string;
}

const CreateAppointmentPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const preselectedPatientId = queryParams.get("patientId");
  const preselectedDate = queryParams.get("date");

  const [patients, setPatients] = useState<Patient[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<FormData>({
    resolver: zodResolver(appointmentSchema),
    defaultValues: {
      patientId: preselectedPatientId || "",
      date: preselectedDate || new Date().toISOString().split("T")[0],
      startTime: "",
      endTime: "",
      doctorId: "",
      reason: "",
      notes: "",
      status: "SCHEDULED",
    },
  });

  // Observer les champs pour mettre à jour automatiquement l'heure de fin
  const watchStartTime = watch("startTime");

  useEffect(() => {
    if (watchStartTime) {
      // Ajoutez 30 minutes par défaut pour la durée du rendez-vous
      try {
        const startTime = new Date(`2000-01-01T${watchStartTime}`);
        const endTime = new Date(startTime.getTime() + 30 * 60000);
        const formattedEndTime = endTime.toTimeString().substring(0, 5);
        setValue("endTime", formattedEndTime);
      } catch (error) {
        console.error("Erreur lors du calcul de l'heure de fin:", error);
      }
    }
  }, [watchStartTime, setValue]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // Récupérer les patients réels
        const realPatients = await patientService.getAllPatients();
        console.log("Patients récupérés:", realPatients);
        setPatients(realPatients);

        // Dans une application réelle, vous auriez un service pour les médecins
        // Pour l'instant, nous utilisons l'ID admin comme seul médecin disponible
        setDoctors([
          {
            id: "00000000-0000-0000-0000-000000000000",
            first_name: "Admin",
            last_name: "Utilisateur",
            role: "ADMIN",
          },
        ]);
      } catch (error) {
        console.error("Erreur lors du chargement des données:", error);
        setError("Erreur lors du chargement des données");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const onSubmit = async (data: FormData) => {
    try {
      setIsSubmitting(true);
      setError(null);

      console.log("Données du formulaire:", data);

      // S'assurer que les formats de date et d'heure sont corrects
      const startDateTime = new Date(`${data.date}T${data.startTime}:00`);
      const endDateTime = new Date(`${data.date}T${data.endTime}:00`);

      // Vérifier que les dates sont valides
      if (isNaN(startDateTime.getTime()) || isNaN(endDateTime.getTime())) {
        throw new Error("Dates ou heures invalides");
      }

      // Formater les dates en ISO pour le backend
      const startISO = startDateTime.toISOString();
      const endISO = endDateTime.toISOString();

      console.log("Date de début formatée:", startISO);
      console.log("Date de fin formatée:", endISO);

      // Formater les données pour l'API
      const appointmentData: AppointmentCreateDto = {
        patientId: data.patientId,
        doctorId: data.doctorId,
        startTime: startISO,
        endTime: endISO,
        reason: data.reason || "Consultation",
        notes: data.notes,
        status: "SCHEDULED",
      };

      console.log("Données envoyées à l'API:", appointmentData);

      // Appel à l'API pour créer le rendez-vous
      const result = await appointmentService.createAppointment(
        appointmentData
      );

      if (result) {
        console.log("Rendez-vous créé avec succès:", result);
        toast.success("Rendez-vous créé avec succès");
        navigate("/appointments");
      } else {
        throw new Error("Échec de la création du rendez-vous");
      }
    } catch (error) {
      console.error("Error creating appointment:", error);
      setError(
        `Une erreur est survenue lors de la création du rendez-vous: ${
          error instanceof Error ? error.message : "Erreur inconnue"
        }`
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-slate-900">
          Créer un nouveau rendez-vous
        </h1>
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="btn btn-outline inline-flex items-center"
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
              d="M10 19l-7-7m0 0l7-7m-7 7h18"
            />
          </svg>
          Retour
        </button>
      </div>

      {error && (
        <Alert variant="error" message={error} onClose={() => setError(null)} />
      )}

      {patients.length === 0 && (
        <Alert
          variant="warning"
          message="Aucun patient n'est disponible. Veuillez d'abord créer un patient avant de planifier un rendez-vous."
          className="mb-4"
        />
      )}

      {/* Formulaire */}
      <div className="card">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Informations de base */}
          <div>
            <h2 className="text-lg font-medium text-slate-900 mb-4">
              Informations du rendez-vous
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <SelectField
                id="patientId"
                label="Patient"
                {...register("patientId")}
                error={errors.patientId?.message}
                options={patients.map((patient) => ({
                  value: patient.id,
                  label: `${patient.firstName} ${patient.lastName}`,
                }))}
                required
              />

              <SelectField
                id="doctorId"
                label="Médecin"
                {...register("doctorId")}
                error={errors.doctorId?.message}
                options={doctors.map((doctor) => ({
                  value: doctor.id,
                  label: `${doctor.first_name} ${doctor.last_name}`,
                }))}
                required
              />

              <InputField
                id="date"
                label="Date"
                type="date"
                {...register("date")}
                error={errors.date?.message}
                required
              />

              <InputField
                id="reason"
                label="Motif du rendez-vous"
                {...register("reason")}
                error={errors.reason?.message}
              />

              <InputField
                id="startTime"
                label="Heure de début"
                type="time"
                {...register("startTime")}
                error={errors.startTime?.message}
                required
              />

              <InputField
                id="endTime"
                label="Heure de fin"
                type="time"
                {...register("endTime")}
                error={errors.endTime?.message}
                required
              />
            </div>
          </div>

          {/* Notes */}
          <div>
            <h2 className="text-lg font-medium text-slate-900 mb-4">Notes</h2>
            <div>
              <label htmlFor="notes" className="label">
                Notes pour le rendez-vous
              </label>
              <textarea
                id="notes"
                rows={4}
                {...register("notes")}
                className="input"
                placeholder="Entrez des notes ou informations supplémentaires pour ce rendez-vous"
              ></textarea>
            </div>
          </div>

          {/* Boutons d'action */}
          <div className="flex justify-end space-x-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate("/appointments")}
              disabled={isSubmitting}
            >
              Annuler
            </Button>
            <Button
              type="submit"
              variant="primary"
              isLoading={isSubmitting}
              disabled={isSubmitting || patients.length === 0}
            >
              {isSubmitting ? "Création en cours..." : "Créer le rendez-vous"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateAppointmentPage;
