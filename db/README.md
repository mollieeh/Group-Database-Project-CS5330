# Database Container Setup (Docker)

Instructions for Docker and MySQL connection setup

## Install Docker Desktop
- https://www.docker.com/products/docker-desktop/

## Start the database & create docker image
```bash
cd db
docker compose up -d
```

## Details for MySQL Connection
- DB name: `degree_db`
- User: `degree_user`
- Password: `degree_password`
- Host port: `57239`


## To Stop the Database Server but keep All Data
```bash
docker compose down
```

## If you make changes to SQL code, then rebuild volume
```bash
docker compose down -v  # stop and delete data volume
docker compose up -d    # rebuild with new db changes
```
