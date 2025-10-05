
init-deps:
	@echo "Initializing the project..."
	@cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@cd frontend && npm install
	@echo "Init Deps."


init-db:
	@echo "Initializing the database..."
	@cd backend && . venv/bin/activate && alembic upgrade head
	@echo "Init DB."


seed-db:
	@echo "Seeding the database with development data..."
	@cd backend && . venv/bin/activate && python3 -m  seeds.dev_data
	@echo "Seed DB."


run-backend:
	@echo "Starting the backend server..."
	@cd backend && . venv/bin/activate && uvicorn main:app --reload
	@echo "Backend server is running."


run-frontend:
	@echo "Starting the frontend server..."
	@cd frontend && npm start
	@echo "Frontend server is running."


