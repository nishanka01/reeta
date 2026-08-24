/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "inverse-on-surface": "#2e3134",
        "inverse-surface": "#e1e2e7",
        "surface-dim": "#111417",
        "surface-container-lowest": "#0c0e12",
        "on-tertiary-container": "#725e00",
        "on-tertiary": "#3b2f00",
        "on-surface": "#e1e2e7",
        "on-primary-fixed": "#002022",
        "surface-container-low": "#191c1f",
        "background": "#111417",
        "surface": "#111417",
        "on-error-container": "#ffdad6",
        "surface-container-highest": "#323539",
        "on-secondary": "#432c00",
        "on-secondary-fixed": "#281900",
        "secondary-fixed": "#ffdeac",
        "surface-container": "#1d2023",
        "tertiary-container": "#fed83a",
        "inverse-primary": "#00696f",
        "surface-variant": "#323539",
        "primary-container": "#00f2ff",
        "outline": "#849495",
        "on-background": "#e1e2e7",
        "on-tertiary-fixed": "#221b00",
        "surface-tint": "#00dbe7",
        "on-primary-container": "#006a71",
        "primary-fixed-dim": "#00dbe7",
        "on-primary": "#00363a",
        "surface-bright": "#37393d",
        "on-surface-variant": "#b9cacb",
        "secondary": "#ffd799",
        "on-primary-fixed-variant": "#004f54",
        "secondary-fixed-dim": "#ffba38",
        "primary-fixed": "#74f5ff",
        "error": "#ffb4ab",
        "tertiary-fixed-dim": "#e8c423",
        "primary": "#e1fdff",
        "tertiary": "#fff6e4",
        "on-secondary-fixed-variant": "#604100",
        "on-tertiary-fixed-variant": "#554500",
        "on-secondary-container": "#6a4800",
        "surface-container-high": "#282a2e",
        "secondary-container": "#feb300",
        "on-error": "#690005",
        "error-container": "#93000a",
        "tertiary-fixed": "#ffe173",
        "outline-variant": "#3a494b"
      },
      borderRadius: {
        "DEFAULT": "0.25rem",
        "lg": "0.5rem",
        "xl": "0.75rem",
        "full": "9999px"
      },
      spacing: {
        "margin-mobile": "20px",
        "gutter": "16px",
        "grid-size": "32px",
        "margin-desktop": "40px",
        "unit": "4px"
      },
      fontFamily: {
        "headline-md": ["Sora", "sans-serif"],
        "display-lg": ["Sora", "sans-serif"],
        "display-lg-mobile": ["Sora", "sans-serif"],
        "data-mono": ["JetBrains Mono", "monospace"],
        "body-md": ["Hanken Grotesk", "sans-serif"],
        "label-caps": ["JetBrains Mono", "monospace"]
      },
      fontSize: {
        "headline-md": ["24px", {"lineHeight": "1.3", "fontWeight": "600"}],
        "display-lg": ["48px", {"lineHeight": "1.1", "letterSpacing": "-0.02em", "fontWeight": "800"}],
        "display-lg-mobile": ["32px", {"lineHeight": "1.2", "fontWeight": "800"}],
        "data-mono": ["14px", {"lineHeight": "1.4", "letterSpacing": "0.05em", "fontWeight": "500"}],
        "body-md": ["16px", {"lineHeight": "1.6", "fontWeight": "400"}],
        "label-caps": ["12px", {"lineHeight": "1", "letterSpacing": "0.1em", "fontWeight": "700"}]
      }
    },
  },
  plugins: [],
}

