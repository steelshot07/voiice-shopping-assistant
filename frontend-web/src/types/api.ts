export interface User {
  id: number;
  email: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface Category {
  id: number;
  name: string;
}

export interface Product {
  id: number;
  name: string;
  brand_id: number;
  category_id: number;
  category_name?: string;
  description?: string;
  price: number;
  currency: string;
  size_value?: number;
  size_unit?: string;
  image_url?: string;
  available?: boolean;
}

export interface ShoppingItem {
  id: number;
  product_id: number;
  quantity: number;
  unit?: string;
  completed: boolean;
  product?: Product;
}

// ── Voice command types ──

export interface ProductOption {
  id: number;
  name: string;
  category?: string;
  price?: string;
  unit?: string;
}

export interface VoiceItemResult {
  product_name: string;
  product_id?: number;
  quantity?: number;
  unit?: string;
  status: "success" | "ambiguous" | "not_found" | "error";
  message: string;
  options?: ProductOption[];
}

export interface VoiceCommandResponse {
  intent: string;
  status: "success" | "ambiguous" | "clarification_needed" | "confirmation_needed" | "error" | "unknown";
  message: string;
  items: VoiceItemResult[];
  confidence: number;
  transcript: string;
  suggestion?: string;
  confirmation_required: boolean;
  context?: Record<string, unknown>;
}
