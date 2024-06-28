Running the Project
Set Up Environment Variables: Create a .env file with your Neo4j connection details.

makefile
Copy code
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
Install Dependencies:

bash
Copy code
pip install -r requirements.txt
Run the Application:

bash
Copy code
uvicorn app.main:app --reload