import { useState, useEffect, useRef } from "react";
import { Search, Plus, Loader2, X } from "lucide-react";
import type { Product } from "../types/api";
import { searchProducts } from "../api/products";

interface SearchBarProps {
  token: string;
  onAddProduct: (productId: number) => void;
}

export function SearchBar({ token, onAddProduct }: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Product[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [addingId, setAddingId] = useState<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Debounced search
  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    setIsSearching(true);
    const timer = setTimeout(async () => {
      try {
        const data = await searchProducts(token, query, undefined, 8);
        setResults(data);
        setIsOpen(data.length > 0);
      } catch {
        setResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query, token]);

  const handleAdd = async (productId: number) => {
    setAddingId(productId);
    try {
      await onAddProduct(productId);
      // Brief feedback then remove from visible results
      setTimeout(() => setAddingId(null), 600);
    } catch {
      setAddingId(null);
    }
  };

  const formatPrice = (product: Product) => {
    const price = Number(product.price);
    if (product.currency === "INR") {
      return `₹${price.toLocaleString("en-IN")}`;
    }
    return `${product.currency} ${price.toFixed(2)}`;
  };

  return (
    <div className="search-bar-container" ref={containerRef}>
      <div className="search-bar">
        <Search size={18} className="search-bar__icon" />
        <input
          type="text"
          className="search-bar__input"
          placeholder="Search groceries..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setIsOpen(true)}
        />
        {isSearching && <Loader2 size={16} className="spinner search-bar__spinner" />}
        {query && !isSearching && (
          <button
            className="search-bar__clear"
            onClick={() => { setQuery(""); setResults([]); setIsOpen(false); }}
            aria-label="Clear search"
          >
            <X size={16} />
          </button>
        )}
      </div>

      {isOpen && results.length > 0 && (
        <div className="search-bar__dropdown">
          {results.map((product) => (
            <div key={product.id} className="search-bar__result">
              <div className="search-bar__result-info">
                <div className="search-bar__result-name">{product.name}</div>
                <div className="search-bar__result-meta">
                  {product.category_name && <span>{product.category_name}</span>}
                  <span>{formatPrice(product)}</span>
                  {product.size_unit && <span>{product.size_value} {product.size_unit}</span>}
                </div>
              </div>
              <button
                className="search-bar__add-btn"
                onClick={() => handleAdd(product.id)}
                disabled={addingId === product.id}
                aria-label={`Add ${product.name}`}
              >
                {addingId === product.id ? (
                  <Loader2 size={16} className="spinner" />
                ) : (
                  <Plus size={16} />
                )}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
