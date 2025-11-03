// medisecure-frontend/src/api/apiClient.ts
import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from "axios";
import { API_URL } from "./endpoints";
import toast from "react-hot-toast";

class ApiClient {
  private static instance: ApiClient;
  private axiosInstance: AxiosInstance;
  private retryCount: number = 0;
  private maxRetries: number = 3;

  private constructor() {
    console.log("Initialisation ApiClient avec URL:", API_URL);

    this.axiosInstance = axios.create({
      baseURL: API_URL,
      headers: {
        "Content-Type": "application/json",
      },
      timeout: 30000, // 30 secondes
      withCredentials: false, // Important: changé à false pour éviter les problèmes CORS
    });
    this.setupInterceptors();
  }

  public static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient();
    }
    return ApiClient.instance;
  }

  private setupInterceptors(): void {
    this.axiosInstance.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem("access_token");
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
          console.log(`Token ajouté à la requête: ${token.substring(0, 20)}...`);
        } else {
          console.warn("Aucun token trouvé dans localStorage");
        }
        console.log(
          `Requête ${config.method?.toUpperCase()} vers ${config.url}`,
          config.data
        );
        console.log("Headers:", config.headers);
        return config;
      },
      (error) => {
        console.error("Erreur lors de la préparation de la requête:", error);
        return Promise.reject(error);
      }
    );

    this.axiosInstance.interceptors.response.use(
      (response) => {
        // Réinitialiser le compteur de tentatives après une réponse réussie
        this.retryCount = 0;
        console.log(`Réponse de ${response.config.url}:`, response.data);
        return response.data; // Retourne directement response.data
      },
      async (error: AxiosError) => {
        if (error.response) {
          console.error(
            `Erreur ${error.response.status} pour ${error.config?.url}:`,
            error.response.data
          );

          if (
            error.response.status === 401 &&
            !error.config?.url?.includes("login")
          ) {
            console.warn("Token expiré ou invalide, déconnexion...");
            localStorage.removeItem("access_token");
            localStorage.removeItem("user");

            if (!window.location.pathname.includes("login")) {
              window.location.href = "/login";
            }
          }
        } else if (
          error.code === "ERR_NETWORK" ||
          error.code === "ECONNABORTED"
        ) {
          // En cas d'erreur réseau, tenter de réessayer automatiquement
          const config = error.config;

          if (config && this.retryCount < this.maxRetries) {
            this.retryCount++;
            console.log(
              `Tentative de reconnexion (${this.retryCount}/${this.maxRetries})...`
            );

            // Ajouter un délai avant de réessayer (backoff exponentiel)
            const delay = Math.pow(2, this.retryCount) * 1000;
            await new Promise((resolve) => setTimeout(resolve, delay));

            // Réessayer la requête
            return this.axiosInstance(config);
          } else {
            // Afficher une notification d'erreur réseau
            toast.error(
              "Impossible de se connecter au serveur. Vérifiez votre connexion réseau."
            );
            console.error(
              "Erreur réseau après plusieurs tentatives:",
              error.message
            );
          }
        } else {
          console.error("Erreur non gérée:", error.message);
        }
        return Promise.reject(error);
      }
    );
  }

  public async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.axiosInstance.get<any, T>(url, config);
      return response;
    } catch (error) {
      console.error(`Erreur GET ${url}:`, error);
      throw error;
    }
  }

  public async post<T>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    try {
      const response = await this.axiosInstance.post<any, T>(url, data, config);
      return response;
    } catch (error) {
      console.error(`Erreur POST ${url}:`, error);
      throw error;
    }
  }

  public async put<T>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    try {
      const response = await this.axiosInstance.put<any, T>(url, data, config);
      return response;
    } catch (error) {
      console.error(`Erreur PUT ${url}:`, error);
      throw error;
    }
  }

  public async patch<T>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    try {
      const response = await this.axiosInstance.patch<any, T>(
        url,
        data,
        config
      );
      return response;
    } catch (error) {
      console.error(`Erreur PATCH ${url}:`, error);
      throw error;
    }
  }

  public async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.axiosInstance.delete<any, T>(url, config);
      return response;
    } catch (error) {
      console.error(`Erreur DELETE ${url}:`, error);
      throw error;
    }
  }
}

export default ApiClient.getInstance();
