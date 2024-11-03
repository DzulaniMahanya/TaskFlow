import os
from flask import Flask, render_template, redirect, request
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

#App setup
app = Flask(__name__)
Scss(app)


#debugging print statement
print("DATABASE_URL:", os.environ.get("DATABASE_URL"))

#configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
db = SQLAlchemy(app)

#initialize database migration
migrate = Migrate(app, db)

# Data Class -> Row of data
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=3))
    status = db.Column(db.String(20), default="In Progress")

    def __repr__(self) -> str:
        return f"Task {self.id}"
    def update_status(self):
        if self.complete:
            self.status = "Completed"
        elif datetime.utcnow() > self.due_date:
            self.status = "Incomplete"
        else:
            self.status = "In Progress"

with app.app_context():
        db.create_all()

#Routes to Webpage(s)
#homepage
@app.route("/", methods=["POST", "GET"])
def index():
    #Add a task
    if request.method == "POST":
        current_task = request.form["content"]
        new_task = Task(content=current_task)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(f"ERROR:{e}")
            return f"ERROR:{e}"
        
    #see all current tasks
    else:
        tasks = Task.query.order_by(Task.created).all()
        return render_template("index.html", tasks=tasks)
    #See all current tasks
    return render_template("index.html")

#Delete item(s)
@app.route("/delete/<int:id>")
def delete(id: int):
    delete_task = Task.query.get_or_404(id)
    try:
        db.session.delete(delete_task)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        return F"ERROR:{e}"
    
#Edit item(s)
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id:int):
    task =  Task.query.get_or_404(id)
    if request.method == "POST":
        task.content = request.form["content"]
        try:
            db.session.commit()
            return redirect("/")
            
        except Exception as e:
            return f"Error:{e}"
    else:
        return render_template("edit.html", task=task)

#Runner and Debugger
if __name__ == "__main__":
    app.run(debug=True)
    