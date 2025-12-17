services:
  postgres:
    image: postgres:16
    restart: always
    environment:
      POSTGRES_USER: kestra
      POSTGRES_PASSWORD: 123@Biotchelly
      POSTGRES_DB: kestra
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U kestra"]
      interval: 10s
      timeout: 5s
      retries: 5

  kestra:
    image: kestra/kestra:latest
    restart: always
    user: "root"
    command: server standalone
    expose:
      - "8080"
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      KESTRA_CONFIGURATION: |
        datasources:
          postgres:
            url: jdbc:postgresql://postgres:5432/kestra
            driverClassName: org.postgresql.Driver
            username: kestra
            password: 123@Biotchelly

        kestra:
          server:
            basic-auth:
              enabled: false
          
          queue:
            type: postgres
          
          repository:
            type: postgres
          
          storage:
            type: local
            local:
              base-path: /app/storage
    volumes:
      - kestra_data:/app/storage
      - /var/run/docker.sock:/var/run/docker.sock

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "8081:80"
    depends_on:
      - kestra
    command: |
      sh -c "echo 'events { worker_connections 1024; }
      http {
        server {
          listen 80;
          location / {
            if (\$$request_method = OPTIONS) {
              add_header Access-Control-Allow-Origin * always;
              add_header Access-Control-Allow-Methods \"GET, POST, OPTIONS, PUT, DELETE\" always;
              add_header Access-Control-Allow-Headers * always;
              add_header Access-Control-Max-Age 1728000;
              add_header Content-Type \"text/plain; charset=utf-8\";
              add_header Content-Length 0;
              return 204;
            }
            add_header Access-Control-Allow-Origin * always;
            add_header Access-Control-Allow-Methods \"GET, POST, OPTIONS, PUT, DELETE\" always;
            add_header Access-Control-Allow-Headers * always;
            add_header Access-Control-Allow-Credentials true always;
            proxy_pass http://kestra:8080;
            proxy_set_header Host \$$host;
            proxy_set_header X-Real-IP \$$remote_addr;
            proxy_set_header X-Forwarded-For \$$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$$scheme;
          }
        }
      }' > /etc/nginx/nginx.conf && nginx -g 'daemon off;'"

volumes:
  kestra_data:
  postgres_data:
