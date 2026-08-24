import { apiRequest } from "./client";
import type { Product, Category } from "../types/api";

export async function searchProducts(
    token: string,
    query?: string,
    categoryId?: number,
    limit?: number,
): Promise<Product[]> {
    const params = new URLSearchParams();
    if (query?.trim()) params.append("q", query);
    if (categoryId) params.append("category_id", categoryId.toString());
    if (limit) params.append("limit", limit.toString());
    
    // If no query and no category and no limit, default to returning popular items
    return apiRequest<Product[]>(`/products?${params.toString()}`, token);
}

export async function getCategories(token: string): Promise<Category[]> {
    return apiRequest<Category[]>(`/categories`, token);
}
