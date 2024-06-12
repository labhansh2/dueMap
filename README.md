# dueMap

This project is a simple Flask web application that allows students to upload
their course schedule/syllabus in any formt with their assignment deadlines. The
app automatically parses the document and adds the assignments, tasks, projects,
and exam deadlines to a Notion Calendar Page for easy progress tracking.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/labhansh2/dueMap.git
    cd dueMap
    ```

2. Create a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up your environment variables in .env.example file and rename it to
   .env.:

    ```plaintext
    OPENAI_API_KEY=your_openai_api_key
    ```

## Usage

1. Run the Flask application:

    ```bash
    python main.py
    ```

2. Open your web browser and go to `http://127.0.0.1:8000`.

3. Refer to
   [How to Use](https://paper-fluorine-b25.notion.site/How-to-use-Assignment-Manager-5068d4a2b50f48be858bd60bca491346?pvs=4)
   Page for more info.

### Happy Assignment Progress Tracking ✨
