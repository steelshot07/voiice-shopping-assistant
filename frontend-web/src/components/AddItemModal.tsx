import React, { useState, useEffect } from "react";
import { X, Search } from "lucide-react";
import type { Product } from "../types/api";
import { searchProducts } from "../api/products";
import { addShoppingItem } from "../api/shopping";

interface AddItemModalProps {
  token: string;
  isOpen: boolean;
  onClose: () => void;
  onItemAdded: () => void;
  defaultCategoryId?: number;
}

function formatPrice(product: Product): string {
  const price = Number(product.price);
  if (product.currency === "INR") {
    return `₹${price.toLocaleString("en-IN")}`;
  }
  return `${product.currency} ${price.toFixed(2)}`;
}

export function AddItemModal({ token, isOpen, onClose, onItemAdded, defaultCategoryId }: AddItemModalProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Product[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [quantity, setQuantity] = useState("1");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    if (!isOpen) {
      setQuery("");
      setResults([]);
      setSelectedProduct(null);
      setQuantity("1");
      setErrorMsg("");
      setIsSubmitting(false);
    }
  }, [isOpen]);

  useEffect(() => {
    const fetchResults = async () => {
      if (!query.trim() && !defaultCategoryId) {
        setResults([]);
        return;
      }
      try {
        const data = await searchProducts(token, query, defaultCategoryId, 10);
        setResults(data);
      } catch {
        // Silent
      }
    };

    const debounce = setTimeout(fetchResults, 300);
    return () => clearTimeout(debounce);
  }, [query, token, defaultCategoryId]);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProduct) return;

    const qtyNum = parseFloat(quantity);
    if (isNaN(qtyNum) || qtyNum <= 0) {
      setErrorMsg("Quantity must be a positive number");
      return;
    }

    setIsSubmitting(true);
    setErrorMsg("");
    try {
      await addShoppingItem(token, selectedProduct.id, qtyNum);
      onItemAdded();
      onClose();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to add item";
      setErrorMsg(message);
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600 }}>Add Item</h2>
          <button className="btn-icon" onClick={onClose}>
            <X size={22} />
          </button>
        </div>

        <form onSubmit={handleAdd}>
          {!selectedProduct ? (
            <div>
              <div style={{ position: 'relative' }}>
                <Search size={18} style={{ position: 'absolute', left: '0.75rem', top: '0.75rem', color: 'var(--text-dim)' }} />
                <input
                  type="text"
                  className="input-field"
                  placeholder="Search products..."
                  style={{ paddingLeft: '2.5rem' }}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  autoFocus
                />
              </div>

              {results.length > 0 && (
                <div className="search-results">
                  {results.map((product) => (
                    <div
                      key={product.id}
                      className="search-result-item"
                      onClick={() => setSelectedProduct(product)}
                    >
                      <div>
                        <div style={{ fontWeight: 500, fontSize: '0.9375rem' }}>{product.name}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                          {product.category_name}
                        </div>
                      </div>
                      <div style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--success)' }}>
                        {formatPrice(product)}{product.size_unit && ` / ${product.size_value} ${product.size_unit}`}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ padding: '0.75rem', backgroundColor: 'var(--background)', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600, fontSize: '1rem' }}>{selectedProduct.name}</span>
                  <button type="button" onClick={() => setSelectedProduct(null)} style={{ color: 'var(--primary)', background: 'none', border: 'none', fontWeight: 500, cursor: 'pointer', fontFamily: 'inherit' }}>Change</button>
                </div>
                <div style={{ fontSize: '0.8125rem', color: 'var(--text-dim)', marginTop: '0.25rem' }}>
                   {formatPrice(selectedProduct)}{selectedProduct.size_unit && ` / ${selectedProduct.size_value} ${selectedProduct.size_unit}`}
                </div>
              </div>

              <div>
                <label className="input-label">Quantity</label>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <input
                    type="number"
                    step="any"
                    className="input-field"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    min="0.1"
                    required
                  />
                  {selectedProduct.size_unit && (
                    <span style={{ color: 'var(--text-dim)', fontSize: '0.875rem' }}>{selectedProduct.size_unit}</span>
                  )}
                </div>
              </div>

              {errorMsg && <div className="error-text">{errorMsg}</div>}

              <button
                type="submit"
                className="btn btn-primary"
                style={{ width: '100%', marginTop: '0.25rem' }}
                disabled={isSubmitting}
              >
                {isSubmitting ? "Adding..." : "Add to List"}
              </button>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
