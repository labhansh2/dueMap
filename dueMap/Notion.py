from notion_client import Client
from pprint import pprint


class Manager:

    db_id = None

    def __init__(self, integration_token: str, page_name: str):

        self.integration_token = integration_token
        self.notion = Client(auth=self.integration_token)
        self.page_name = page_name

        self.page_id = self.get_page()

    def get_page(self):

        target_page = self.notion.search(
            query=self.page_name, **{
                "object": "page",
                'parent': {'type': 'workspace', 'workspace': True}
            },
        )

        # pprint(target_page)

        if len(target_page['results']) == 0:
            raise ValueError('Page Not Found')
        else:
            for page in target_page['results']:
                if (page['parent'] == {'type': 'workspace', 'workspace': True} and
                        (page['properties']['title']['title'][0]['plain_text']).lower() == self.page_name.lower()):

                    return page['id']

            raise ValueError('Page Not Found')

    def get_user_name(self):

        # users = self.notion.users.list()
        # print(users)

        # incomplete
        # needs authentication
        return r"${user}"

    def get_db_parent_status(self, db_parent):

        if db_parent == {'page_id': self.page_id, 'type': 'page_id'}: 
            return True
        
        # print(db_parent, end=" :: ")

        while db_parent['type'] == 'block_id':

            block = self.notion.blocks.retrieve(block_id=db_parent['block_id'])

            # print(block['parent'], end=" :: ")

            if block['parent'] == {'page_id': self.page_id, 'type': 'page_id'}:
                return True
            
            db_parent = block['parent']
            
        return False
    
    def get_database(self, db_name: str):

        db = self.notion.search(filter={
            "property": "object", "value": "database"
        })

        # pprint(db)

        if len(db['results']) == 0:
            raise ValueError("No Database Found")

        else:
            for database in db['results']:
                print((database['title'][0]['plain_text']).lower(), end=" :: ")
                print(self.get_db_parent_status(database['parent']))
                if (self.get_db_parent_status(database['parent'])
                        and (database['title'][0]['plain_text']).lower() == db_name.lower()):
                    
                    
                    self.db_id = database['id']
                    return database['id']
            raise ValueError("No Database Found2")

    def create_database(self, db_name):

        database_properties = {
            'Assignment': {
                'name': 'Task Name',
                'title': {},
                'type': 'title'
            },
            'Status': {
                'name': 'Status',
                'select': {
                    'options': [
                        {
                            'color': 'green',
                            'name': 'Done ✅'
                        },
                        {
                            'color': 'gray',
                            'name': 'Not Started'
                        },
                        {
                            'color': 'yellow',
                            'name': 'In Progress 🛩️'
                        },
                        {
                            'color': 'red',
                            'name': 'Overdue 🔴'
                        }
                    ]
                },
                'type': 'select'
            },
            "Course": {
                "name": "Course",
                # "type": "rich_text",
                # "rich_text": {}
                "type": "select",
                "select": {
                    'options': []
                }
            },
            'Date': {
                'date': {},
                'name': 'Date',
                'type': 'date'
            }}

        db = self.notion.databases.create(
            title=[
                {
                    'annotations': {
                        'bold': False,
                        'code': False,
                        'color': 'default',
                        'italic': False,
                        'strikethrough': False,
                        'underline': False
                    },
                    'href': None,
                    'plain_text': db_name,
                    'text': {
                        'content': db_name,
                        'link': None
                    },
                    'type': 'text'
                }
            ],
            parent={"type": "page_id", "page_id": self.page_id},
            properties=database_properties,
            is_inline=False
        )

        self.db_id = db['id']

        return db

    def add_assignment(self, assignment_obj, course_name):

        props2 = {
            'Date': {
                'type': 'date',
                'date': {
                    'end': None,
                    'start': assignment_obj["deadline"],
                    'time_zone':  "US/Central"
                }
            },

            'Assignment': {
                'title': [
                    {
                        'plain_text': 'newly added '
                        'task',
                        'text': {
                            'content': assignment_obj["assignment_name"],
                            'link': None
                        },
                        'type': 'text'
                    }
                ],
                'type': 'title'
            },

            'Course': {

                "type": "select",
                "select": {"name": course_name}
            },

            'Status': {
                'select': {"name": "Not Started"},
                'type': 'select'
            }
        }

        self.notion.pages.create(
            parent={
                'database_id': self.db_id, 'type': 'database_id'
            },
            properties=props2
        )


if __name__ == "__main__":

    m = Manager('secret_', 'General')

    print(m.page_id)
    print()
    print()

    d = m.get_database('Tasks')
    print(d)

    m.add_assignment({'assignment_name': 'Lab 1',
                  'deadline': '2024-09-12T00:00:00'}, 'ANTH 105')

    ...
    # manager = Manager(
    #     'secret_key', 'Assignmets')
    # manager.get_database()
    # manager.get_user_name()
