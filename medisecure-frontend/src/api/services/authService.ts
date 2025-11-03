// src/api/services/authService.ts
import apiClient from "../apiClient";
import { ENDPOINTS } from "../endpoints";

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    role: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
  };
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface ResetPasswordRequest {
  email: string;
}

const authService = {
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    try {
      console.log("Tentative de connexion avec:", credentials);

      // Transformer les données pour correspondre à ce qu'attend FastAPI OAuth2
      const formData = new URLSearchParams();
      formData.append("username", credentials.username);
      formData.append("password", credentials.password);

      // Configuration spéciale pour le format attendu par FastAPI OAuth2
      const config = {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      };

      // Appel API avec les bons en-têtes
      const response = await apiClient.post<LoginResponse>(
        ENDPOINTS.AUTH.LOGIN,
        formData.toString(),
        config
      );

      console.log("Réponse d'authentification reçue:", response);

      // Stocker le token
      if (response.access_token) {
        localStorage.setItem("access_token", response.access_token);
        // Stocker les informations de l'utilisateur
        localStorage.setItem("user", JSON.stringify(response.user));
        console.log("Token stocké dans localStorage:", response.access_token.substring(0, 20) + "...");
        
        // Vérifier que le token a bien été stocké
        const storedToken = localStorage.getItem("access_token");
        console.log("Vérification du token stocké:", storedToken ? "✓ Token trouvé" : "✗ Token NON trouvé");
      } else {
        throw new Error("Token non reçu dans la réponse");
      }

      return response;
    } catch (error) {
      console.error("Erreur d'authentification:", error);
      throw error;
    }
  },

  logout: async (): Promise<void> => {
    try {
      await apiClient.post(ENDPOINTS.AUTH.LOGOUT);
    } finally {
      // Nettoyer le localStorage même si la requête échoue
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user");
    }
  },

  resetPassword: async (data: ResetPasswordRequest): Promise<void> => {
    await apiClient.post(ENDPOINTS.AUTH.RESET_PASSWORD, data);
  },

  isAuthenticated: (): boolean => {
    return !!localStorage.getItem("access_token");
  },
};

export default authService;
