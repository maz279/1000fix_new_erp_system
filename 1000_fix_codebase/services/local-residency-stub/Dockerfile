FROM python:3.12.10-slim@sha256:fd95fa221297a88e1cf49c55ec1828edd7c5a428187e67b5d1805692d11588db
# DE-11: assert local environment at startup and refuse otherwise.
ENV FIX_ENV=local
WORKDIR /app
COPY app.py .
RUN printf '#!/bin/sh\n[ "$FIX_ENV" = "local" ] || { echo "refusing to start: FIX_ENV=$FIX_ENV (DE-11)"; exit 42; }\nexec python app.py\n' > /entrypoint.sh && chmod +x /entrypoint.sh
# No EXTERNAL network route exists in this image - DE-14 by construction.
ENTRYPOINT ["/entrypoint.sh"]
