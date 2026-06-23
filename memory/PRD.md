# Mercato Maestro — PRD

## Original Problem Statement
Dashboard di intelligence calciomercato deploy-ata su **GitHub Pages** (sito statico, single-file HTML).
Requisiti chiave: design carbone+oro, lettura notizie inline, dati Transfermarkt live, AdSense,
SEO, favorites, filtri temporali, notifiche browser.

## Architecture (Static)
```
/app/
├── index.html            # App principale (CSS + JS inline)
├── about.html            # Chi siamo
├── contact.html          # Contatti (Formspree/Buttondown)
├── privacy.html          # GDPR
├── cookies.html          # GDPR cookies
├── manifest.json         # PWA manifest
├── sw.js                 # Service Worker (cache-first assets, network-first HTML/JSON)
├── feed.xml              # RSS feed
├── news.json             # Dataset notizie (template)
├── logo.png              # 512x512 — gold M + ball + lightning
├── logo-192.png          # PWA icon
├── apple-touch-icon.png  # 180x180
├── favicon-32.png        # 32x32
├── og-image.jpg          # 1200x630 social preview
├── robots.txt
└── sitemap.xml
```

## Implemented (febbraio 2026)

### Phase 1 — base SEO/compliance/UX
- ✅ Palette "Carbone + Oro Champagne" + tipografia editoriale (Bebas Neue / Inter / IBM Plex Mono)
- ✅ Logo SVG iniziale (sostituito poi con asset PNG)
- ✅ Modal lettura notizie inline + auto-linking entità → Transfermarkt API
- ✅ AdSense `ca-pub-4053268187610276` (3 slot)
- ✅ GDPR cookie banner + localStorage consent
- ✅ Filtri temporali (24h/3g/7g/tutto)
- ✅ Favorites in localStorage (stella ⭐)
- ✅ Notifiche browser (campanella 🔔)
- ✅ about.html + contact.html + privacy.html + cookies.html
- ✅ robots.txt + sitemap.xml base

### Phase 2 — pacchetto "Ottimo" (3 feb 2026)
- ✅ **Nuovo logo PNG** (gold M + soccer ball + lightning bolt su sfondo nero)
  - Variants: logo.png (512), logo-192.png, apple-touch-icon.png (180), favicon-32.png
  - Aggiornato in tutte le pagine + JSON-LD + favicon
- ✅ **Hero section** in homepage con tagline e contatori live (news/campionati/24-7)
  - Gradient + griglia di sfondo + logo flottante animato
- ✅ **Dark / Light mode toggle** con icona sole/luna nel topbar
  - Persistenza localStorage `mm_theme`
  - Rispetta `prefers-color-scheme` al primo accesso
  - Light theme = "carta da giornale" beige
  - Aggiornamento dinamico `meta[theme-color]`
- ✅ **PWA installabile**
  - `manifest.json` con shortcuts (News / Preferiti)
  - `sw.js` service worker (network-first per HTML/JSON, cache-first per assets)
  - Registrazione automatica al `window.load`
- ✅ **RSS feed** (`feed.xml`) + `<link rel="alternate">` nel `<head>`
- ✅ **OG image dinamica** (1200×630) generata con il nuovo logo + tagline
- ✅ **Placeholder analytics** in `<head>`:
  - GA4 (`G-XXXXXXXXXX` da sostituire)
  - Microsoft Clarity (`YOUR_CLARITY_ID`)
  - Google Search Console (`INCOLLA_QUI_IL_CODICE_VERIFICA`)

## Roadmap

### P1
- Sitemap.xml dinamica con build script
- Sostituzioni manuali su GitHub: email contatto, ID Formspree, ID Buttondown, slot AdSense

### P2 (future)
- Storage Cloudflare R2/S3 per immagini articoli
- Newsletter integrata (Buttondown lead capture)
- Quote di trading di mercato (Stripe per donazioni?)

## Test Credentials
N/A — sito 100% statico, nessun login.

## Stack
HTML5 + CSS3 + Vanilla JS. Zero build, zero framework, zero backend.
