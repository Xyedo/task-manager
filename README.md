# Task Manager

A simple drag and drop task manager for personal projects. have a multiple workspaces and CRUD task.

## Features

- Create, read, update, delete (CRUD) tasks
- Manages Workspaces
- Interactive UI

## Prerequisites

- Node.js >= 20
- Python == 3.10.13 (use asdf to manage python version)
- (Linux) libpq-dev
- Make (or just copy and paste the command in Makefile)

## Development

1.  to initializes all of the dependencies run

```zsh
make init-deps
```

2. fill the env

```
  cp backend/.env.example backend/.env
```

3. initializes development container

```zsh
docker compose up -d
```

4. initialized database migration

```zsh
make init-db
```

5. seed the data with development data

```zsh
make seed-db
```

6. in separate terminal window run

```zsh

make run-backend
```

the backend process will run in localhost:8000

```zsh
make run-frontend
```

the frontend process will run in port localhost:5173
