import { Home, Mic, ShoppingCart } from "lucide-react";

type Tab = "home" | "voice" | "list";

interface BottomNavProps {
  activeTab: Tab;
  onTabChange: (tab: Tab) => void;
  listCount?: number;
}

export function BottomNav({ activeTab, onTabChange, listCount = 0 }: BottomNavProps) {
  return (
    <nav className="bottom-nav" aria-label="Main navigation">
      <button
        className={`bottom-nav__tab ${activeTab === "home" ? "bottom-nav__tab--active" : ""}`}
        onClick={() => onTabChange("home")}
        aria-label="Home"
      >
        <Home size={20} />
        <span>Home</span>
      </button>

      <button
        className="bottom-nav__tab bottom-nav__tab--voice"
        onClick={() => onTabChange("voice")}
        aria-label="Voice command"
      >
        <div className="bottom-nav__voice-ring">
          <Mic size={22} />
        </div>
        <span>Voice</span>
      </button>

      <button
        className={`bottom-nav__tab ${activeTab === "list" ? "bottom-nav__tab--active" : ""}`}
        onClick={() => onTabChange("list")}
        aria-label="Shopping list"
      >
        <div style={{ position: "relative" }}>
          <ShoppingCart size={20} />
          {listCount > 0 && (
            <span className="bottom-nav__badge">{listCount > 99 ? "99+" : listCount}</span>
          )}
        </div>
        <span>List</span>
      </button>
    </nav>
  );
}
