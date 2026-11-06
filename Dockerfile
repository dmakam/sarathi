# Sarathi: build the static site from the pinned public-domain dataset,
# then serve it with a small internal Caddy (port 80, no TLS; the shared
# signal-desk-app Caddy terminates TLS and proxies to this container).

FROM python:3.12-alpine AS build
ARG GITA_COMMIT=c6fce39595445768876ddbb8d1268a9c935e1d2b
WORKDIR /app
ADD https://github.com/gita/gita/archive/${GITA_COMMIT}.tar.gz /tmp/gita.tar.gz
RUN mkdir -p src-data && tar -xzf /tmp/gita.tar.gz -C src-data --strip-components=1 && rm /tmp/gita.tar.gz
COPY build ./build
COPY assets ./assets
ARG SARATHI_BASE_URL=https://sarathi.dhirajmakam.com
ENV SARATHI_BASE_URL=${SARATHI_BASE_URL}
RUN python3 -I build/build.py

FROM caddy:2-alpine
COPY Caddyfile.app /etc/caddy/Caddyfile
COPY --from=build /app/site /srv
EXPOSE 80
