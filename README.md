# COEN424-A2

COEN424 Assignment 2

## Run monolith container (all services in one image)

Build the Docker image (PowerShell):

```powershell
docker build -t coen424-monolith:latest .
```

Run the services with Docker Compose (recommended).

This will start RabbitMQ (official image with management UI) and build+run the monolith image. Your MongoDB is expected to be external (for example MongoDB Atlas) and the monolith will read the connection string from environment.

```powershell
docker compose up --build
# (or, if you use the older CLI)
docker-compose up --build
```

After compose finishes starting, the endpoints will be available on the host as before, and RabbitMQ management UI on http://localhost:15672 (guest/guest).

If you run `docker compose up --build` you'll need to provide your MongoDB connection string via environment. Create a `.env` file in the repo (not checked in) with values like:

```text
# .env (example - DO NOT COMMIT SECRETS)
MONGO_URI=mongodb+srv://<user>:<pass>@cluster0.mongodb.net/mydb?retryWrites=true&w=majority
MONGO_URL=${MONGO_URI}
# Optional: override RabbitMQ credentials (defaults are guest/guest)
RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest
```

Then run:

```powershell
docker compose up --build
```

If you prefer a single Docker image that includes RabbitMQ (not recommended for production), you can build and run the "single-image" monolith which runs RabbitMQ and the Python services together under Supervisor.

Build the single-image (this image bundles RabbitMQ and the app):

```powershell
docker build -t coen424-monolith:single .
```

Run the single-image (exposes RabbitMQ ports and management UI):

```powershell
docker run --rm -p 8080:8080 -p 8001:8001 -p 8002:8002 -p 8003:8003 -p 5672:5672 -p 15672:15672 --name coen424-monolith-single coen424-monolith:single
```

Notes when running the single-image:

- RabbitMQ will run inside the container; startup can take a few seconds. The order service includes retry/backoff logic so it will wait for RabbitMQ.
- To persist broker data across runs, mount a volume for `/var/lib/rabbitmq`:

```powershell
docker run --rm -v rabbit_data:/var/lib/rabbitmq -p 5672:5672 -p 15672:15672 coen424-monolith:single
```

Prefer the Compose option for local dev. Use the single-image only if you have a specific distribution constraint.

Service endpoints after container is running:

- Gateway: http://localhost:8080/
- User v1 API: http://localhost:8001/api/
- Order service API: http://localhost:8002/api/
- User v2 API: http://localhost:8003/api/

Notes:

- The monolith image uses Supervisor to run the Python service processes (gateway, user services, order service) inside the container. Logs are forwarded to container stdout/stderr. RabbitMQ is provided by the separate `rabbit` service in Compose.
- RabbitMQ management UI will be available at http://localhost:15672 (default guest/guest) unless you override credentials.
- If you want to change routing percentages, edit `gateway/gateway_config.json` before building.
