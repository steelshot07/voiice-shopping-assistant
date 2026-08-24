export const API_URL = import.meta.env.VITE_API_URL || "";

export async function apiRequest<T>(
    path: string,
    token: string,
    options: RequestInit = {},
): Promise<T> {
    const response = await fetch(`${API_URL}${path}`, {
        ...options,
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
            "ngrok-skip-browser-warning": "true",
            ...options.headers,
        },
    });

    if (!response.ok) {
        let errorMessage = "API Error";
        try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
            errorMessage = `HTTP Error ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
    }

    if (response.status === 204) {
        return undefined as unknown as T;
    }

    return response.json();
}
