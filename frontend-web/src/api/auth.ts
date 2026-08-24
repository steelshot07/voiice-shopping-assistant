import { API_URL } from "./client";
import type { Token } from "../types/api";

export async function login(email: string, password: string): Promise<Token> {
    const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            "ngrok-skip-browser-warning": "true",
        },
        body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
        throw new Error("Invalid credentials");
    }

    return response.json();
}

export async function register(email: string, password: string): Promise<any> {
    const response = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            "ngrok-skip-browser-warning": "true",
        },
        body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
        if (response.status === 409) {
            throw new Error("User already exists");
        }
        throw new Error("Registration failed");
    }

    return response.json();
}
