// El Membrillo — Tailwind config compartido (CDN). Cargar DESPUÉS del script de Tailwind CDN.
tailwind.config = {
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Marca
        "primary": "#8B0000",         // vino membrillo
        "primary-hover": "#6B0000",
        "primary-deep": "#610000",
        "gold": "#D4A574",            // acento dorado
        "gold-soft": "#FFE082",
        "bg-cream": "#FAF6F0",        // fondo
        "card-cream": "#F5E6D3",      // cards
        "text-dark": "#2C1810",
        "text-muted": "#6B5B4F",
        // Estado
        "success-green": "#4CAF50",
        "warning-amber": "#FFA726",
        "error-red": "#E53935",
        // Material tonal (heredado del sistema Stitch)
        "surface": "#fff8f6",
        "surface-variant": "#f8dcd8",
        "on-surface": "#261816",
        "on-surface-variant": "#5a403c",
        "outline": "#8e706b",
        "outline-variant": "#e3beb8",
        "primary-container": "#8b0000",
        "secondary-container": "#fecb97",
        "secondary": "#7c572d",
        "primary-fixed": "#ffdad4",
        "primary-fixed-dim": "#ffb4a8",
        // Sidebar oscuro
        "sidebar": "#2C1810",
        "sidebar-hover": "#3d2417",
      },
      fontFamily: {
        "display": ["Playfair Display", "serif"],
        "headline-md": ["Playfair Display", "serif"],
        "headline-lg": ["Playfair Display", "serif"],
        "price-lg": ["Playfair Display", "serif"],
        "body": ["Inter", "system-ui", "sans-serif"],
        "body-md": ["Inter", "system-ui", "sans-serif"],
        "eyebrow": ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        "soft": "0 4px 20px rgba(139,0,0,0.08)",
        "lift": "0 12px 32px rgba(139,0,0,0.16)",
        "fab": "0 10px 30px rgba(139,0,0,0.3)",
      },
      maxWidth: { "container": "1280px" },
    },
  },
};
