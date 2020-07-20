import os
import sys
import json
import pandas as pd
from botocore.exceptions import EndpointConnectionError


DEFAULT_OUTPUT_FILE = 'output.json'

class Solution:

    FILES = ['teachers.parquet', 'students.csv']

    def __init__(self, location):
        self.location = location
        self.result = None
        self.__run()
    
    @classmethod
    def from_local_decrectory(cls, local='.'):
        """
        Named constructor as a class method for initiating the object with local file system
        @params: local(str) - path of local directory
        @return: obj{Solution} - Object of Solution class
        """
        cls.__scan_local_files(local)
        return cls(local)

    @classmethod
    def from_s3(cls, path):
        """
        Named constructor as a class method for initiating the object with S3 bucket path
        @params: local(str) - path of S3 bucket
        @return: obj{Solution} - Object of Solution class
        """
        return cls(path)
        
    def get_result(self):
        """
        Returns the result
        @params: None
        @return: {dict}
        """
        return self.result

    @staticmethod
    def __scan_local_files(path):
        """
        Scans the input directory for validation
        @params: path(str) - path of local directory
        @return: None
        """
        local_files=os.listdir(path)
        if Solution.FILES[0] not in local_files or Solution.FILES[1] not in local_files:
            print('.'*50)
            print(f'Error: {Solution.FILES[0]} or {Solution.FILES[1]} not found in your local system,')
            print('.'*50)
            print()
            sys.exit(1)

    def __run(self):
        """
        Encapsulated internal method which invokes the self.__genearte_result and also handles the S3 Error
        @params: None
        @return: None
        """
        try:
            self.__generate_result()
        except EndpointConnectionError:
            print("Please configure your aws cli on this system")
        except Exception:
            print('Something went wrong..')

    def __inner_join(self, row, students):
        """
        Joins the teacher and student object into one teachers object with list of student as per class id
    
        @params: row(Dataframe) - Teacher pandas Dataframe
        @params: students(Dataframe) - Students pandas Dataframe
        @return: dict: Populated dictionary
        """
        tmp = {
            'teacher_id': row['id'],
            'teacher_name': row['fname'] + ' ' + row['lname'],
                'cid': row['cid']
        }
        tmp['students'] = []
        for _, r in students[students['cid'] == row['cid']].iterrows():
            tmp['students'].append({'student_id': r['id'], 'student_name': r['fname'] + ' ' + r['lname'] })
        return tmp


    def __generate_result(self):
        """
        Generates the output file in a json format
        @params: None
        @return: None
        """
        teachers, students = None, None
        for file in Solution.FILES:
            if file.endswith('.parquet'):
                teachers = pd.read_parquet(
                    self.location + '/teachers.parquet',
                                        engine='pyarrow')
            elif file.endswith('.csv'):
                students = pd.read_csv(
                    self.location + '/students.csv', delimiter='_')
        parse_data = [self.__inner_join(row, students) for _, row in teachers.iterrows()]
        self.result = parse_data
        data = json.dumps(parse_data, indent=4)
        with open(DEFAULT_OUTPUT_FILE, 'w') as file:
                file.write(data)
        print('output.json file generated successfully...')


if __name__ == "__main__":
    print('\nPlease choose one option \n')
    print('1. From local\n2. From S3\n\n3. Exit')
    choice = input('> ')
    if choice == '1':
        print('Hit enter for current directory or provide path to directory where you have students.csv & teachers.parquet files.')
        path = input('> ')
        sol = Solution.from_local_decrectory(path if path != '' else '.')
    elif choice == '2':
        print('Please enter your valid s3 path of directory where you have students.csv & teachers.parquet files.')
        path = input('> ')
        sol = Solution.from_s3(path)
    else:
        print('Thanks..')
        sys.exit(0)
