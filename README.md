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


## Backend Architecture

My Backend Architecture is a Ortogonal Architecture that consist of three layers 
  
  Infrastructure(Http Framework, Databases, TokenManager)
  Usecases(Business Logic Orchestration)
  Domain(Business Unit)

## API Design Decisions


I created the Frontend with mock data to know what data should i store, so the API follows that principle

It has two Domain:
  1. Identity
    - It Has Tenant With Many Users
    - It Also Do Authentication with:
      - JWT Access Token (short lived)
      - JWT Payload is composed of user_id, tenant_id, and username to make validation and query easier
      - Refresh Token (long lived, saved in the db)
      - Login, and Logout to generate and revoke those token


  2. Workspaces
    - Workspace has Multiple Group, Group has Multiple Task, Task can be transition or changed between those groups, Task can assigned to User within the same Tenant

    - Group can be generic, it can just to group task, or it can be a status based, in the next iteration we should add the validation on task transition between those groups

  Based on those two Domains, I designed the API that consist of identity and workspaces
  - POST identity/Login
    - handle username and password and return the JWT accessToken and JWT refreshToken
    - on accessToken, it has 60 seconds TTL
    - on refreshToken, it has 1 month of TTL, whenever accessToken expires, we need to generate again based on refreshToken

  - PUT identity/refresh: to refresh accessToken based on refreshToken
  - DELETE identity/logout: revoke refreshToken
  - GET identity/users: get users based on the same tenant
  - GET identity/me: helper method to get all of user identifier


  - GET workspaces: List of all workspaces within tenant
  - POST workspaces: create workspaces and the default group
  - GET workspaces/by-name/{workspace-name}: get workspaces by name because workspace name within the company is unique

  - PUT workspaces/{workspaceId}/groups/{groupId}: Update Group
  - POST workspaces/{workspaceId}/groups/{groupId}/task: Create Task
  - GET workspaces/{workspaceId}/groups/{groupId}/task/{taskId}: Get Task
  - PATCH workspaces/{workspaceId}/groups/{groupId}/task/{taskId}: Update Task detail, and group which task belongs to
  - PATCH workspaces/{workspaceId}/groups/{groupId}/task/{taskId}: Delete Task

## Testing Methodology
  
  Due to Nature of this Assignments, the Methodology i've used is Manual End to End testing from frontend and backends


  we should have to develop Unit Test on Each Usecases with database mocks,
  Handler test on Usecase mocks and add integration test that that handles users flow

  Because the Architecture of My Backend application is Ortogonal Architecture. its extensible to add unit test in the next iteration 



## API Performance and Optimization
  the API Performance is has p99 under 100ms on Normal Load doing basic User flow
  
  The Optimization we can do when the scale coming is:

  1. if it Server Problem: Horizontal Scaling the Server because statelessness of REST API is safe to scale


  2. if it Database read Problem, Add Index on Hot Path Query , if not sufficient, add Redis as intermediary cache on the databases
    
  
  3. if it a Database write problem, Add Queue to persistent the request and add optimistic UI to smooth the delay and backend consume the queue, if it still cannot handle the scale, switch databases with NoSQL databases



## Security Vulnerablities
  1. Allow Headers and Allow Method on CORS is wildcards, it should be based on Priciple of least priviege and add it to environtment variable to make changes easier
  
  2. No AccessToken Expiry in Development

  3. Env Var is not validated, it should be class of Config the group those env var and validate the env var



## Performance Blockage
  Because Task and Group can be accessed with many users, race condition might happened

  we Need to implement Lock to make the other users wait if the resources still being updated by other users and do last writes wins within valid condition


## Security Measures
  I do User Level Authentication based on Stateless JWT Token to validate request and Input Output Validation to make sure the result are expected


## Security Impact on Performance
  Security Impact on Performance in REST application is just a noise compared to database contention and IO Bound with result on p99 still under 100ms
