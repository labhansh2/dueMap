from flask import Flask, render_template, url_for, request, redirect, jsonify
import json
from notion_client import errors
import os
import threading
import time
from pprint import pprint

from dueMap import Notion
from dueMap import aiParser

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

notion_client = None

logs = []
completed = False


@app.route("/")
@app.route("/home")
def home():

    return render_template('home.html', title="DueMap", subtitle="Connect with your Notion")


@app.route("/submit-notion-info", methods=["POST"])
def handle_notion_auth():

    global notion_client

    notion_integration_token = request.form.get('integration_token')
    notion_page_name = request.form.get('page_name')
    notion_db_name = request.form.get('db_name')

    try:
        notion_client = Notion.Manager(
            notion_integration_token, notion_page_name)
    except ValueError as error:

        return render_template('home.html', title="DueMap",
                               subtitle="Connect with your Notion", error=error)
    except errors.APIResponseError as error:
        return render_template('home.html', title="DueMap",
                               subtitle="Connect with your Notion", error=error)
    else:

        try:
            _ = notion_client.get_database(notion_db_name)
        except:
            notion_client.create_database(notion_db_name)
            return redirect(url_for('add_course'))
        else:
            return redirect(url_for('add_course'))


@app.route("/add-course")
def add_course():

    completed = False
    return render_template('add_course.html',
                           title="Add Course",
                           subtitle=f"Welcome, {notion_client.get_user_name()}")


@app.route("/submit-course-details", methods=["POST"])
def handle_course():

    course_name = request.form.get('course_name')
    file = request.files.get('course_syllabus_file')

    if file and file.filename:

        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # run the thread here
        thread = threading.Thread(
            target=add_assignments, args=(course_name, file_path))
        thread.start()

        return render_template('add_assgn.html')
    else:
        return render_template('add_course.html',
                               title="Add Course",
                               subtitle=f"Welcome, {notion_client.get_user_name()}", error="No File Uploaded")


def add_assignments(course_name, file_path):

    global logs, completed
    logs = []
    completed = False

    # save the file object in open ai api

    logs.append("Setting Up the parser...")
    parser = aiParser.Parser()

    logs.append("Sending file to the parser...")
    parser.create_message(file_path=file_path)

    logs.append("Parsing the document...")
    partial_parse = parser.get_parsed_data()

    pprint(partial_parse)

    logs.append("Parsing the document content...")
    final_parse = aiParser.final_parse(partial_parse=partial_parse)

    # pprint(final_parse)

    final_parse_obj = json.loads(final_parse)

    pprint(final_parse_obj)

    try:
        final_schema = final_parse_obj["assignments"]
    except:
        final_schema = final_parse_obj
    
    logs.append("\nAdding Assignments...")

    for assignment in final_parse_obj["assignments"]:

        logs.append(assignment["assignment_name"])

        try:

            notion_client.add_assignment(
                assignment_obj=assignment, course_name=course_name)

        except:

            logs.append("Error while adding this task!")
            try:
                logs.append("Trying again...")
                notion_client.add_assignment(
                    assignment_obj=assignment, course_name=course_name)
            except Exception as e:
                logs.append(
                    f"{e} : While adding {assignment['assignment_name']} :: {assignment['deadline']}")

    completed = True


@app.route("/logs")
def adding_assignments():

    global logs, completed

    redirect_url = url_for('add_course')
    return jsonify({'logs': logs, 'completed': completed, 'redirect_url': redirect_url})


if __name__ == '__main__':

    app.run(debug=True)
