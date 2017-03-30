import os


root_dir = os.path.abspath(os.path.dirname(__file__))

infos = {
         'name': 'bruker2nifti',
         'version': '0.0.0',
         'description': 'From raw brukert to nifty, home-made converter.',
         'web_infos' : '',
         'repository': {
                        'type': 'git',
                        'url': ''
                       },
         'author': 'sebastiano ferraris',
         'author_email': 'sebastiano.ferraris@gmail.com',
         'dependencies': {
                          # requirements.txt file automatically generated using pipreqs.
                          'python' : '{0}/requirements.txt'.format(root_dir)
                          }
         }