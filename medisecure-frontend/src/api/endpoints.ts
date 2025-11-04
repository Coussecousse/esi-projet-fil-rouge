// medisecure-frontend/src/api/endpoints.ts

// Extend Window interface to include our environment variables
declare global {
  interface Window {
    _env_?: {
      VITE_API_URL?: string;
    };
  }
}

// Use relative path for API since Nginx will proxy requests
// This allows the frontend to make requests to /api which Nginx will forward to the backend
export const API_URL = "/api";

console.log('Using API_URL:', API_URL);

export const ENDPOINTS = {
  AUTH: {
    LOGIN: "/auth/login",
    LOGOUT: "/auth/logout",
    REFRESH: "/auth/refresh",
    RESET_PASSWORD: "/auth/reset-password",
  },
  PATIENTS: {
    BASE: "/patients/",
    DETAIL: (id: string) => `/patients/${id}`,
    SEARCH: "/patients/search",
  },
  APPOINTMENTS: {
    BASE: "/appointments/",
    DETAIL: (id: string) => `/appointments/${id}`,
    BY_PATIENT: (patientId: string) => `/appointments/patient/${patientId}`,
    BY_DOCTOR: (doctorId: string) => `/appointments/doctor/${doctorId}`,
    CALENDAR: "/appointments/calendar",
  },
  MEDICAL_RECORDS: {
    BASE: "/medical-records/",
    DETAIL: (id: string) => `/medical-records/${id}`,
    DOCUMENTS: (recordId: string) => `/medical-records/${recordId}/documents`,
    DOCUMENT: (recordId: string, documentId: string) =>
      `/medical-records/${recordId}/documents/${documentId}`,
  },
};
