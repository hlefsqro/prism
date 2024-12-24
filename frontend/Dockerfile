FROM caddy:alpine

COPY Caddyfile /etc/caddy/Caddyfile

COPY out /usr/share/caddy

EXPOSE 80

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile"]
