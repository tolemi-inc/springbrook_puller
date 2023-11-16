import tableauserverclient as TSC
import time
import json
import traceback
import argparse

parser = argparse.ArgumentParser(
    description='Process inputs to pull from springbrook')

parser.add_argument('--config', type=str, help='Path to config file')

args = parser.parse_args()


def start_server(username, pat):
    # PAT = Personal Access Token
    # PAT Name, PAT Value, SiteName
    tableau_auth = TSC.PersonalAccessTokenAuth(
        username, pat, 'MountVernonNY2110')
    server = TSC.Server(
        'https://analytics.springbrooksoftware.com', use_server_version=True)
    return server, tableau_auth


def dlReportbyID(server, tableau_auth, id, data_file_path):  # Retrieve data and write to file
    with server.auth.sign_in(tableau_auth):
        report_view = server.views.get_by_id(id)
        server.views.populate_csv(report_view, req_options=None)
        with open(data_file_path, 'wb') as f:
            f.write(b''.join(report_view.csv))
            # print ("Retrieval complete.")
        server.auth.sign_out()


def run(config):
    start_t = time.time()

    pat = config.pat
    username = config.username
    data_file_path = config.data_file_path

    server, tableau_auth = start_server(username, pat)
    report_id = "0d5f855b-588b-4a4a-9c88-00daf260c510"  # Static workbook ID
    report_view_id = 'b1c1613b-7fcc-48ba-8d03-4b659a8334cb'  # Static workbook 'view' ID

    # dumpReportsbyID(server, tableau_auth, report_id)
    dlReportbyID(server, tableau_auth, report_view_id, data_file_path)
    execution_t = (time.time() - start_t)

    # get headers and remove them from the output csv
    with open(data_file_path, 'r+') as f:
        headers_string = f.readline().strip()
        headers_list = headers_string.split(',')
        headers_dict = [{'name': header, 'type': 'VARCHAR'} for header in headers_list]

        all_lines = f.readlines()
        data_lines = all_lines[1:-1]

        f.seek(0)
        f.truncate()
        f.writelines(data_lines)

    # print("execution time: " + str(execution_t / 60))

    output_object = {'status': 'ok',
                     'file_name': data_file_path, 'columns': headers_dict}
    print('DONE', json.dumps(output_object))


def fail(error):
    result = {
        "status": "error",
        "error": """{}
         {}""".format(str(error), traceback.format_exc())
    }

    output_json = json.dumps(result)
    print('DONE', output_json)


def load_config(file_path):
    raw_config = load_json(file_path)
    print('RAW CONFIG', raw_config)

    data_file_path = raw_config.get('dataFilePath', None)

    sub_config = raw_config.get('config')
    pat = sub_config.get('personal access token', None)
    username = sub_config.get('username', None)
    

    return Config(pat, username, data_file_path)


def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        True
        print(f"File '{file_path}' not found.")
    except json.JSONDecodeError as e:
        True
        print(f"JSON decoding error: {e}")
    except Exception as e:
        True
        print(f"An error occurred: {e}")


class ConfigError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Config:
    def __init__(self, pat, username, data_file_path):
        self.pat = pat
        self.username = username
        self.data_file_path = data_file_path

    @ property
    def pat(self):
        return self._pat

    @ pat.setter
    def pat(self, value):
        if value is None:
            raise ConfigError("Missing pat in config")
        else:
            self._pat = value

    @ property
    def username(self):
        return self._username

    @ username.setter
    def username(self, value):
        if value is None:
            raise ConfigError("Missing username in config")
        else:
            self._username = value

    @ property
    def data_file_path(self):
        return self._data_file_path

    @ data_file_path.setter
    def data_file_path(self, value):
        if value is None:
            raise ConfigError("Missing data file path in config.")
        else:
            self._data_file_path = value


# Main Program
if __name__ == "__main__":
    try:
        config = load_config(args.config)
        run(config)
    except ConfigError as e:
        fail(e)
