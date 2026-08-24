import { apiRequest } from "./client";
import type { ShoppingItem } from "../types/api";

export async function getShoppingItems(token: string): Promise<ShoppingItem[]> {
    return apiRequest<ShoppingItem[]>("/items", token);
}

export async function addShoppingItem(
    token: string,
    productId: number,
    quantity: number = 1,
): Promise<ShoppingItem> {
    return apiRequest<ShoppingItem>("/items", token, {
        method: "POST",
        body: JSON.stringify({ product_id: productId, quantity }),
    });
}

export async function updateShoppingItem(
    token: string,
    itemId: number,
    updates: { quantity?: number; completed?: boolean },
): Promise<ShoppingItem> {
    return apiRequest<ShoppingItem>(`/items/${itemId}`, token, {
        method: "PATCH",
        body: JSON.stringify(updates),
    });
}

export async function deleteShoppingItem(
    token: string,
    itemId: number,
): Promise<void> {
    await apiRequest<void>(`/items/${itemId}`, token, {
        method: "DELETE",
    });
}
