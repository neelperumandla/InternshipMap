from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Resume(db.Model):
    __tablename__ = "resumes"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=True)
    skills = db.Column(db.JSON, nullable=False)
    projects = db.Column(db.JSON, nullable=False)
    experience = db.Column(db.JSON, nullable=False)

    def __repr__(self):
        return f"<Resume {self.id} - {self.email}>"