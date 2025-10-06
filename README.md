# Task Manager

A simple drag and drop task manager for personal projects. have a multiple workspaces and CRUD task.

## Features
- Create, read, update, delete (CRUD) tasks
- Manages Workspaces
- Interactive UI

## Prerequisites
- Node.js >= 20
- Python >= 3.13
- Make


## Development

1. to initializes all of the dependencies run

```zsh
make init-deps
```
1. fill the env
```
  cp backend/.env.example backend/.env
```


1. initializes development container
```zsh
docker compose up -d
```


1. initialized database migration
```zsh
make init-db
```

1. seed the data with development data
```zsh
make seed-db
```

1. in separate terminal window run
```zsh

make run-backend 
```
the backend process will run in localhost:8000


```zsh
make run-frontend
```
the frontend process will run in port localhost:5173




