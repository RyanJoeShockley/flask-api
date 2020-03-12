from flask import Flask, render_template, flash, request, make_response
import json
import connexion

app = connexion.App(__name__, specification_dir="./")
app.add_api("swagger.yml")


@app.route("/")
def home():
	return render_template("home.html")

if __name__ == "__main__":
    app.run()
