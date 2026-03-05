import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Shield } from "lucide-react"; // Using Lucide for a minimal logo

const navLinks = [
  { to: "/", label: "Home" },
  { to: "/upload", label: "Analysis" },
  { to: "/history", label: "History" },
];

export default function NavBar() {
  const location = useLocation();

  return (
    <nav className="sticky top-0 z-50 apple-nav border-b border-zinc-200/50 flex items-center justify-between px-6 py-4 md:px-12 transition-all duration-300">
      <Link to="/" className="flex items-center gap-2 group outline-none">
        <Shield className="w-6 h-6 text-zinc-900 group-hover:text-zinc-600 transition-colors" strokeWidth={1.5} />
        <span className="text-xl font-semibold tracking-tight text-zinc-900 group-hover:text-zinc-600 transition-colors">
          TrustChain
        </span>
      </Link>

      <div className="flex items-center gap-8">
        {navLinks.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className={cn(
              "text-sm font-medium transition-all duration-300 outline-none",
              location.pathname === link.to
                ? "text-zinc-900 tracking-wide"
                : "text-zinc-500 hover:text-zinc-900 hover:tracking-wide"
            )}
          >
            {link.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}
