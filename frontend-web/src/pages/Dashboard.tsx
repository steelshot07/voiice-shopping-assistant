import { useState, useEffect, useCallback } from "react";
import {
  LogOut, Plus, Trash2, Loader2, Sparkles, Grid, Check, Minus, User,
  Leaf, Droplet, Coffee, Utensils, Heart, Home, Snowflake, Archive, Package, ShoppingCart
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { getShoppingItems, updateShoppingItem, deleteShoppingItem, addShoppingItem } from "../api/shopping";
import { searchProducts, getCategories } from "../api/products";
import type { ShoppingItem, Product, Category } from "../types/api";
import { VoiceButton } from "../components/VoiceButton";
import { AddItemModal } from "../components/AddItemModal";
import { SearchBar } from "../components/SearchBar";
import { BottomNav } from "../components/BottomNav";

// Category icon map (frontend-only)
const getCategoryIcon = (categoryName: string, size = 20) => {
  switch (categoryName) {
    case "Produce": return <Leaf size={size} />;
    case "Dairy": return <Droplet size={size} />;
    case "Bakery": return <Utensils size={size} />;
    case "Beverages": return <Coffee size={size} />;
    case "Snacks": return <Heart size={size} />;
    case "Personal Care": return <Sparkles size={size} />;
    case "Household": return <Home size={size} />;
    case "Frozen": return <Snowflake size={size} />;
    case "Staples": return <Archive size={size} />;
    default: return <Package size={size} />;
  }
};

function formatPrice(price: number, currency: string = "INR"): string {
  if (currency === "INR") {
    return `₹${Number(price).toLocaleString("en-IN")}`;
  }
  return `${currency} ${Number(price).toFixed(2)}`;
}

export function Dashboard() {
  const { token, signOut } = useAuth();
  const [items, setItems] = useState<ShoppingItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [popularProducts, setPopularProducts] = useState<Product[]>([]);

  const [isLoading, setIsLoading] = useState(true);
  const [isAddingPopular, setIsAddingPopular] = useState<number | null>(null);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [defaultCategoryId, setDefaultCategoryId] = useState<number | undefined>();
  const [errorMsg, setErrorMsg] = useState("");

  const [activeTab, setActiveTab] = useState<"home" | "voice" | "list">("home");
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  const fetchItems = useCallback(async () => {
    if (!token) return;
    try {
      const data = await getShoppingItems(token);
      setItems(data);
      setErrorMsg("");
    } catch {
      setErrorMsg("Failed to load shopping list.");
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  const fetchDiscoveryData = useCallback(async () => {
    if (!token) return;
    try {
      const [cats, pops] = await Promise.all([
        getCategories(token),
        searchProducts(token, "", undefined, 10),
      ]);
      setCategories(cats);
      setPopularProducts(pops);
    } catch {
      // Silent fallback
    }
  }, [token]);

  useEffect(() => {
    fetchItems();
    fetchDiscoveryData();
  }, [fetchItems, fetchDiscoveryData]);

  const toggleComplete = async (item: ShoppingItem) => {
    if (!token) return;
    const originalItems = [...items];
    setItems(items.map(i => i.id === item.id ? { ...i, completed: !i.completed } : i));

    try {
      await updateShoppingItem(token, item.id, { completed: !item.completed });
    } catch {
      setItems(originalItems);
    }
  };

  const deleteItem = async (id: number) => {
    if (!token) return;
    const originalItems = [...items];
    setItems(items.filter(i => i.id !== id));

    try {
      await deleteShoppingItem(token, id);
    } catch {
      setItems(originalItems);
    }
  };

  const updateQty = async (item: ShoppingItem, delta: number) => {
    if (!token) return;
    const newQty = Number(item.quantity) + delta;
    if (newQty < 1) return;
    const originalItems = [...items];
    setItems(items.map(i => i.id === item.id ? { ...i, quantity: newQty } : i));

    try {
      await updateShoppingItem(token, item.id, { quantity: newQty });
    } catch {
      setItems(originalItems);
    }
  };

  const handleAddPopular = async (productId: number) => {
    if (!token) return;
    setIsAddingPopular(productId);
    try {
      await addShoppingItem(token, productId, 1);
      await fetchItems();
    } catch {
      // Silent
    } finally {
      setIsAddingPopular(null);
    }
  };

  const handleSearchAdd = async (productId: number) => {
    if (!token) return;
    try {
      await addShoppingItem(token, productId, 1);
      await fetchItems();
    } catch {
      // Silent
    }
  };

  const openCategoryAdd = (categoryId: number) => {
    setDefaultCategoryId(categoryId);
    setIsModalOpen(true);
  };

  const openManualAdd = () => {
    setDefaultCategoryId(undefined);
    setIsModalOpen(true);
  };

  const activeItems = items.filter(i => !i.completed);
  const completedItems = items.filter(i => i.completed);
  const activeCount = activeItems.length;
  const completedCount = completedItems.length;
  const isEmpty = items.length === 0;

  // Estimated total
  const estimatedTotal = activeItems.reduce((sum, item) => {
    const price = item.product?.price ? Number(item.product.price) : 0;
    return sum + (price * Number(item.quantity));
  }, 0);

  // Handle voice tab: activate the voice button
  const handleTabChange = (tab: "home" | "voice" | "list") => {
    if (tab === "voice") {
      // Programmatic click on the voice button
      const voiceBtn = document.getElementById("voice-command-button");
      if (voiceBtn) voiceBtn.click();
      return;
    }
    setActiveTab(tab);
  };

  // ── Render list view ──
  const renderShoppingList = () => (
    <div className="shopping-list-section">
      <div className="section-header">
        <h2 className="section-title">Shopping List</h2>
        {activeCount > 0 && (
          <span className="section-badge">{activeCount} item{activeCount !== 1 ? "s" : ""}</span>
        )}
      </div>

      {isEmpty ? (
        <div className="empty-state">
          <div className="empty-state__icon"><ShoppingCart size={48} /></div>
          <h3>Your shopping list is ready</h3>
          <p>Start by saying <strong>"Add milk"</strong> or browse popular items below.</p>
        </div>
      ) : (
        <>
          {/* Active items */}
          {activeItems.map(item => (
            <div key={item.id} className="shopping-item">
              <button
                className={`shopping-item__check ${item.completed ? "shopping-item__check--done" : ""}`}
                onClick={() => toggleComplete(item)}
                aria-label={item.completed ? "Mark incomplete" : "Mark complete"}
              >
                {item.completed && <Check size={14} />}
              </button>
              <div className="shopping-item__content" onClick={() => toggleComplete(item)}>
                <div className="shopping-item__name">{item.product?.name || "Unknown Item"}</div>
                <div className="shopping-item__meta">
                  {item.product?.category_name && <span>{item.product.category_name}</span>}
                  {item.product?.price && <span>{formatPrice(Number(item.product.price), item.product.currency)}</span>}
                </div>
              </div>
              <div className="shopping-item__qty-controls">
                <button className="qty-btn" onClick={() => updateQty(item, -1)} disabled={Number(item.quantity) <= 1} aria-label="Decrease">
                  <Minus size={14} />
                </button>
                <span className="shopping-item__qty">{Number(item.quantity)}{item.unit ? ` ${item.unit}` : ""}</span>
                <button className="qty-btn" onClick={() => updateQty(item, 1)} aria-label="Increase">
                  <Plus size={14} />
                </button>
              </div>
              <button onClick={() => deleteItem(item.id)} className="shopping-item__delete" aria-label="Delete">
                <Trash2 size={16} />
              </button>
            </div>
          ))}

          {/* Completed items */}
          {completedItems.length > 0 && (
            <div className="completed-section">
              <div className="completed-section__header">
                <span>Completed ({completedCount})</span>
              </div>
              {completedItems.map(item => (
                <div key={item.id} className="shopping-item shopping-item--completed">
                  <button
                    className="shopping-item__check shopping-item__check--done"
                    onClick={() => toggleComplete(item)}
                    aria-label="Mark incomplete"
                  >
                    <Check size={14} />
                  </button>
                  <div className="shopping-item__content" onClick={() => toggleComplete(item)}>
                    <div className="shopping-item__name">{item.product?.name || "Unknown Item"}</div>
                  </div>
                  <button onClick={() => deleteItem(item.id)} className="shopping-item__delete" aria-label="Delete">
                    <Trash2 size={16} />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Estimated total */}
          {estimatedTotal > 0 && (
            <div className="list-total">
              <span>Estimated Total</span>
              <span className="list-total__amount">{formatPrice(estimatedTotal)}</span>
            </div>
          )}

          <button
            onClick={openManualAdd}
            className="btn btn-secondary add-manual-btn"
          >
            <Plus size={18} /> Add Manually
          </button>
        </>
      )}
    </div>
  );

  // ── Render home view ──
  const renderHome = () => (
    <div className="dashboard-content">
      {/* Voice Hero */}
      <div className={`voice-hero ${!isEmpty ? "voice-hero--compact" : ""}`}>
        <div className="voice-hero__text">
          <h2>{isEmpty ? "Shop smarter with your voice" : "Need something?"}</h2>
          {isEmpty && <p>Tell me what you need and I'll add it to your list.</p>}
        </div>

        <div className="voice-hero__action">
          {token && <VoiceButton token={token} onCommandSuccess={fetchItems} mode="hero" />}
        </div>

        {isEmpty && (
          <div className="hero-suggestions">
            <div className="suggestion-chip">"Add 2 apples"</div>
            <div className="suggestion-chip">"I need milk and eggs"</div>
            <div className="suggestion-chip">"Add 1 kg rice"</div>
          </div>
        )}
      </div>

      {/* Current list preview (when items exist) */}
      {!isEmpty && (
        <div className="section-padded">
          <div className="section-header">
            <h3 className="section-title">Current List</h3>
            <button className="section-link" onClick={() => setActiveTab("list")}>
              View all ({activeCount})
            </button>
          </div>
          {activeItems.slice(0, 3).map(item => (
            <div key={item.id} className="shopping-item-compact">
              <button
                className={`shopping-item__check ${item.completed ? "shopping-item__check--done" : ""}`}
                onClick={() => toggleComplete(item)}
                aria-label={item.completed ? "Mark incomplete" : "Mark complete"}
              >
                {item.completed && <Check size={12} />}
              </button>
              <span className="shopping-item-compact__name">{item.product?.name}</span>
              <span className="shopping-item-compact__qty">×{Number(item.quantity)}</span>
            </div>
          ))}
          {activeCount > 3 && (
            <button className="section-link" onClick={() => setActiveTab("list")} style={{ marginTop: "0.5rem" }}>
              +{activeCount - 3} more items
            </button>
          )}
        </div>
      )}

      {/* Popular Items */}
      <div className="section-padded">
        <div className="section-header">
          <h3 className="section-title"><Sparkles size={16} /> Popular Items</h3>
        </div>
        <div className="horizontal-scroll">
          {popularProducts.map(product => (
            <div key={product.id} className="product-card" onClick={() => handleAddPopular(product.id)}>
              {isAddingPopular === product.id ? (
                <Loader2 size={24} className="spinner" color="var(--primary)" style={{ margin: "auto" }} />
              ) : (
                <>
                  <div className="product-card__icon">{getCategoryIcon(product.category_name || "", 18)}</div>
                  <div className="product-card__name">{product.name}</div>
                  <div className="product-card__meta">{product.category_name}</div>
                  <div className="product-card__price">{formatPrice(Number(product.price), product.currency)}</div>
                  {product.size_unit && (
                    <div className="product-card__unit">{product.size_value} {product.size_unit}</div>
                  )}
                  <div className="product-card__add"><Plus size={16} /></div>
                </>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Shop by Category */}
      <div className="section-padded">
        <div className="section-header">
          <h3 className="section-title"><Grid size={16} /> Shop by Category</h3>
        </div>
        <div className="category-grid">
          {categories.map(cat => (
            <div key={cat.id} className="category-tile" onClick={() => openCategoryAdd(cat.id)}>
              <div className="category-tile__icon">{getCategoryIcon(cat.name, 24)}</div>
              <span className="category-tile__name">{cat.name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Additions */}
      {popularProducts.length > 5 && (
        <div className="section-padded">
          <div className="section-header">
            <h3 className="section-title">Quick Additions</h3>
          </div>
          <div className="quick-add-grid">
            {popularProducts.slice(5, 10).map(product => (
              <button
                key={product.id}
                className="quick-add-chip"
                onClick={() => handleAddPopular(product.id)}
                disabled={isAddingPopular === product.id}
              >
                {isAddingPopular === product.id ? <Loader2 size={14} className="spinner" /> : <Plus size={14} />}
                {product.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div>
          <h1>My Groceries</h1>
          <div className="header__stats">
            {activeCount} active • {completedCount} completed
          </div>
        </div>
        <div className="header__actions">
          <div className="profile-menu-container">
            <button
              className="btn-icon"
              onClick={() => setShowProfileMenu(!showProfileMenu)}
              aria-label="Profile"
            >
              <User size={20} />
            </button>
            {showProfileMenu && (
              <div className="profile-menu">
                <button onClick={() => { signOut(); setShowProfileMenu(false); }}>
                  <LogOut size={16} /> Sign Out
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Search */}
      {token && (
        <div className="search-section">
          <SearchBar token={token} onAddProduct={handleSearchAdd} />
        </div>
      )}

      {/* Error banner */}
      {errorMsg && (
        <div className="error-banner">
          {errorMsg}
        </div>
      )}

      {/* Main content */}
      {isLoading ? (
        <div style={{ display: "flex", justifyContent: "center", padding: "3rem" }}>
          <Loader2 className="spinner" size={32} color="var(--primary)" />
        </div>
      ) : (
        activeTab === "list" ? renderShoppingList() : renderHome()
      )}

      {/* FAB voice button (shown on list tab) */}
      {activeTab === "list" && !isEmpty && token && (
        <VoiceButton token={token} onCommandSuccess={fetchItems} mode="fab" />
      )}

      {/* Bottom Nav */}
      <BottomNav
        activeTab={activeTab}
        onTabChange={handleTabChange}
        listCount={activeCount}
      />

      {/* Add item modal */}
      {token && (
        <AddItemModal
          token={token}
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onItemAdded={fetchItems}
          defaultCategoryId={defaultCategoryId}
        />
      )}
    </div>
  );
}
