# Bakery Tracker in a container.
#
# The app keeps ALL of its data in one folder (the database plus backups),
# pointed at by BAKERY_DATA_DIR. Mount that folder from outside the container
# and nothing is ever lost when the container is rebuilt.
FROM node:22-alpine

WORKDIR /app
COPY bakery/ ./bakery/

# Everything the business owns lives here; the host mounts a volume on it.
ENV BAKERY_DATA_DIR=/data
VOLUME ["/data"]

# First start on an empty volume seeds demo data. For a real bakery, start once
# with -e BAKERY_SEED=empty and use the first-run setup wizard instead.
ENV BAKERY_SEED=demo

EXPOSE 3000
WORKDIR /app/bakery

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD wget -q -O /dev/null http://127.0.0.1:3000/api/status || exit 1

CMD ["node", "--disable-warning=ExperimentalWarning", "server/index.js"]
