// src/api/services/appointmentService.ts
import apiClient from "../apiClient";
import { ENDPOINTS } from "../endpoints";

export interface Appointment {
  id: string;
  patientId: string;
  doctorId: string;
  startTime: string;
  endTime: string;
  status: "SCHEDULED" | "CONFIRMED" | "CANCELLED" | "COMPLETED";
  reason?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface AppointmentCreateDto {
  patientId: string;
  doctorId: string;
  startTime: string;
  endTime: string;
  reason?: string;
  notes?: string;
  status?: "SCHEDULED" | "CONFIRMED" | "CANCELLED" | "COMPLETED";
}

export interface AppointmentUpdateDto {
  status?: "SCHEDULED" | "CONFIRMED" | "CANCELLED" | "COMPLETED";
  startTime?: string;
  endTime?: string;
  reason?: string;
  notes?: string;
}

export interface AppointmentFilter {
  patientId?: string;
  doctorId?: string;
  date?: string;
  status?: "SCHEDULED" | "CONFIRMED" | "CANCELLED" | "COMPLETED";
  startDate?: string;
  endDate?: string;
}

// Fonction pour adapter les appointements du back-end vers le front-end
const adaptAppointmentFromApi = (backDto: any): Appointment => {
  return {
    id: backDto.id,
    patientId: backDto.patient_id,
    doctorId: backDto.doctor_id,
    startTime: backDto.start_time,
    endTime: backDto.end_time,
    status: backDto.status,
    reason: backDto.reason,
    notes: backDto.notes,
    createdAt: backDto.created_at,
    updatedAt: backDto.updated_at,
  };
};

// Fonction pour adapter les DTO de création du front vers le back
const adaptAppointmentCreateDto = (frontDto: AppointmentCreateDto): any => {
  try {
    console.log("Adaptation des données du rendez-vous:", frontDto);

    return {
      patient_id: frontDto.patientId,
      doctor_id: frontDto.doctorId,
      start_time: frontDto.startTime,
      end_time: frontDto.endTime,
      reason: frontDto.reason || "Consultation",
      notes: frontDto.notes,
      status: frontDto.status, 
    };
  } catch (error) {
    console.error("Erreur lors de l'adaptation des données:", error);
    throw error;
  }
};

// Fonction pour adapter les DTO de mise à jour
const adaptAppointmentUpdateDto = (frontDto: AppointmentUpdateDto): any => {
  const backDto: any = {};

  if (frontDto.status !== undefined) backDto.status = frontDto.status;
  if (frontDto.startTime !== undefined) backDto.start_time = frontDto.startTime;
  if (frontDto.endTime !== undefined) backDto.end_time = frontDto.endTime;
  if (frontDto.reason !== undefined) backDto.reason = frontDto.reason;
  if (frontDto.notes !== undefined) backDto.notes = frontDto.notes;

  return backDto;
};

// Interface pour la réponse de liste
interface AppointmentListResponse {
  appointments: any[];
  total: number;
  skip: number;
  limit: number;
}

const appointmentService = {
  getAllAppointments: async (
    filter?: AppointmentFilter
  ): Promise<Appointment[]> => {
    try {
      // On utilise une approche différente pour construire l'URL avec les paramètres
      let queryParams = new URLSearchParams();

      if (filter) {
        if (filter.patientId) queryParams.append("patientId", filter.patientId);
        if (filter.doctorId) queryParams.append("doctorId", filter.doctorId);
        if (filter.date) queryParams.append("date", filter.date);
        if (filter.status) queryParams.append("status", filter.status);
        if (filter.startDate) queryParams.append("startDate", filter.startDate);
        if (filter.endDate) queryParams.append("endDate", filter.endDate);
      }

      const url = `${ENDPOINTS.APPOINTMENTS.BASE}?${queryParams.toString()}`;
      console.log("Fetching appointments with URL:", url);

      const response = await apiClient.get<AppointmentListResponse>(url);
      console.log("API Response for appointments:", response);
      return response.appointments.map(adaptAppointmentFromApi);
    } catch (error) {
      console.error("Error fetching appointments:", error);
      // Retourner un tableau vide en cas d'erreur plutôt que de planter
      return [];
    }
  },

  getAppointmentById: async (id: string): Promise<Appointment | null> => {
    try {
      const response = await apiClient.get<any>(
        ENDPOINTS.APPOINTMENTS.DETAIL(id)
      );
      return adaptAppointmentFromApi(response);
    } catch (error) {
      console.error(`Error fetching appointment ${id}:`, error);
      return null;
    }
  },

  getAppointmentsByPatient: async (
    patientId: string
  ): Promise<Appointment[]> => {
    try {
      const response = await apiClient.get<AppointmentListResponse>(
        ENDPOINTS.APPOINTMENTS.BY_PATIENT(patientId)
      );
      return response.appointments.map(adaptAppointmentFromApi);
    } catch (error) {
      console.error(
        `Error fetching appointments for patient ${patientId}:`,
        error
      );
      return [];
    }
  },

  getAppointmentsByDoctor: async (doctorId: string): Promise<Appointment[]> => {
    try {
      const response = await apiClient.get<AppointmentListResponse>(
        ENDPOINTS.APPOINTMENTS.BY_DOCTOR(doctorId)
      );
      return response.appointments.map(adaptAppointmentFromApi);
    } catch (error) {
      console.error(
        `Error fetching appointments for doctor ${doctorId}:`,
        error
      );
      return [];
    }
  },

  getAppointmentsCalendar: async (
    year: number,
    month: number
  ): Promise<Appointment[]> => {
    try {
      // Utilisation du format de requête avec paramètres pour éviter les erreurs 405
      const queryParams = new URLSearchParams({
        year: year.toString(),
        month: month.toString(),
      });

      const url = `${
        ENDPOINTS.APPOINTMENTS.CALENDAR
      }?${queryParams.toString()}`;
      console.log("Fetching calendar with URL:", url);

      const response = await apiClient.get<AppointmentListResponse>(url);
      return response.appointments.map(adaptAppointmentFromApi);
    } catch (error) {
      console.error(`Error fetching calendar for ${year}/${month}:`, error);
      return [];
    }
  },

  createAppointment: async (
    appointment: AppointmentCreateDto
  ): Promise<Appointment | null> => {
    try {
      const adaptedAppointment = adaptAppointmentCreateDto(appointment);
      console.log("Creating appointment with data:", adaptedAppointment);

      // Augmenter le timeout pour cette requête spécifique
      const response = await apiClient.post<any>(
        ENDPOINTS.APPOINTMENTS.BASE,
        adaptedAppointment,
        { timeout: 30000 }
      );

      console.log("Appointment created successfully:", response);
      return adaptAppointmentFromApi(response);
    } catch (error) {
      console.error("Error creating appointment:", error);
      throw error; // Renvoyer l'erreur pour un meilleur traitement côté UI
    }
  },

  updateAppointment: async (
    id: string,
    appointment: AppointmentUpdateDto
  ): Promise<Appointment | null> => {
    try {
      const adaptedAppointment = adaptAppointmentUpdateDto(appointment);
      console.log(`Updating appointment ${id} with data:`, adaptedAppointment);
      const response = await apiClient.put<any>(
        ENDPOINTS.APPOINTMENTS.DETAIL(id),
        adaptedAppointment,
        { timeout: 30000 }
      );
      console.log("Appointment updated successfully:", response);
      return adaptAppointmentFromApi(response);
    } catch (error) {
      console.error(`Error updating appointment ${id}:`, error);
      return null;
    }
  },

  cancelAppointment: async (
    id: string,
    reason?: string
  ): Promise<Appointment | null> => {
    try {
      const response = await apiClient.put<any>(
        ENDPOINTS.APPOINTMENTS.DETAIL(id),
        {
          status: "CANCELLED",
          notes: reason,
        }
      );
      console.log(`Appointment ${id} CANCELLED successfully`);
      return adaptAppointmentFromApi(response);
    } catch (error) {
      console.error(`Error cancelling appointment ${id}:`, error);
      return null;
    }
  },

  confirmAppointment: async (id: string): Promise<Appointment | null> => {
    try {
      const response = await apiClient.put<any>(
        ENDPOINTS.APPOINTMENTS.DETAIL(id),
        {
          status: "CONFIRMED",
        }
      );
      console.log(`Appointment ${id} CONFIRMED successfully`);
      return adaptAppointmentFromApi(response);
    } catch (error) {
      console.error(`Error confirming appointment ${id}:`, error);
      return null;
    }
  },

  completeAppointment: async (id: string): Promise<Appointment | null> => {
    try {
      const response = await apiClient.put<any>(
        ENDPOINTS.APPOINTMENTS.DETAIL(id),
        {
          status: "COMPLETED",
        }
      );
      console.log(`Appointment ${id} marked as COMPLETED`);
      return adaptAppointmentFromApi(response);
    } catch (error) {
      console.error(`Error completing appointment ${id}:`, error);
      return null;
    }
  },
};

export default appointmentService;
