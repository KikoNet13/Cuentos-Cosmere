# Frontend SPA

SPA en `Vue + Vite` para la biblioteca interactiva y la vista de cuento.

## Scripts

- `npm ci`
- `npm run dev`
- `npm run build`

## Build de produccion

La salida se genera en `../app/static/spa/` con archivos fijos:

- `assets/app.js`
- `assets/app.css`

Flask sirve esos archivos desde `app/templates/spa_shell.html`.
