# Construction en deux étapes : l'étape « build » compile les fichiers
# statiques (Node), l'étape finale ne contient plus que Nginx pour les servir
# — l'image de production n'embarque ni Node ni le code source, seulement le
# résultat de `vite build`.
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
# VITE_API_URL est lu par Vite À LA COMPILATION (import.meta.env), pas au
# démarrage du conteneur : doit donc être fourni comme argument de build,
# pas comme variable d'environnement du conteneur final (qui ne fait plus
# tourner de code JavaScript capable de la lire).
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

FROM nginx:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
