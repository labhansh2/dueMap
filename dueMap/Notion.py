from notion_client import Client
# from pprint import pprint


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
                "object": "page"
            }
        )

        if len(target_page['results']) == 0:
            raise ValueError('Page Not Found')
        else:
            return target_page['results'][0]['id']

    def get_user_name(self):
        # users = self.notion.users.list()
        # print(users)

        # incomplete 
        # needs authentication
        return r"${user}"

    def get_database(self):

        db = self.notion.search(filter={
            "property":"object", "value":"database"
        })

        if len(db['results']) == 0:
            raise ValueError("No Database Found")
        elif db['results'][0]['parent']['page_id'] != self.page_id:
            raise ValueError("No Database Found for The Page")
        else:
            self.db_id = db['results'][0]['id']
            return db['results'][0]['id']

    def create_database(self):

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
                "select" : {
                    'options':[]
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
                        'plain_text': 'Assignments',
                        'text': {
                            'content': 'Assignments',
                            'link': None
                        },
                        'type': 'text'
                    }
                ],
                parent={"type": "page_id", "page_id": self.page_id},
                properties=database_properties,
                is_inline=True
            )
        
        self.db_id = db['id']

        return db
    
    def add_assignment(self, assignment_obj, course_name):

        # prop={'Date': {
        #     'type': 'date',
        #     'date': {'start': assignment_obj["deadline"],
        #     'end': None,
        #     'time_zone': "US/Central"}},
        #     'Status': {
        #     'type': 'multi_select',
        #     'multi_select': [{
        #         'name': 'Not started'}]},
        #     'Course': {
        #     'type': 'select',
        #     'multi_select': [{'name': course_name}]},
        #     'Assignment': {'id': 'title',
        #     'type': 'title',
        #     'title': [{'type': 'rich_text',
        #         'text': {'content': assignment_obj["assignment_name"], 'link': None},
        #         'href': None}]}}


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
                # 'type': 'rich_text',
                # 'rich_text': [
                #     {
                #     'type':'text',
                #     'text':{
                #         'content': course_name
                #   }
                # }
                # ]
                "type" : "select",
                "select": {"name" : course_name}
            },

            'Status': {
                'select': { "name" : "Not Started"} ,
                'type': 'select'
            }
        }

        
        self.notion.pages.create(
            parent={
                'database_id':self.db_id, 'type':'database_id'
            },
            properties=props2
        )


if __name__ == "__main__":

    ...

    # manager = Manager(
    #     'secret_key', 'Assignmets')
    # manager.get_database()
    # manager.get_user_name()