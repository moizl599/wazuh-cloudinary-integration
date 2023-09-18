# Import env file module
# ==============================
from dotenv import load_dotenv
load_dotenv()
# Import the Cloudinary libraries
# ==============================
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Import to format the JSON responses
# ==============================
import json
import os
# Set your Cloudinary credentials
# ==============================
config = cloudinary.config(secure=True)


class API_calls:
    def __init__(self):
        logfile = "logfile.log"
        reported_asset_list = '/opt/wazuh_logging/cloudinary/reported_asset_list.txt'
        test_logfile = '/opt/wazuh_logging/cloudinary/generic_log_file.log'
        resource_types = ['image', 'video', 'raw']
        # API call to cloudinary for pulling the resources
        self.logfile = logfile
        self.reported_asset_list = reported_asset_list
        self.resource_types = resource_types
        self.test_logfile = test_logfile

    def project_fall_back(self):
        # function to make sure the generic log file is always there
        test_logfile = self.test_logfile
        if os.path.isfile(test_logfile):
            print("fairenough")
        else:
            with open(test_logfile, 'x') as f:
                print("all good now pheww")

    def call_cloudinary(self):
        # Declaring log files
        reported_asset_list = self.reported_asset_list
        resource_types = self.resource_types
        test_logfile = self.test_logfile

        for resource_type in resource_types:
            # removing the log file to make sure new logs are written on the file.
            logfile = f"/opt/wazuh_logging/cloudinary/{resource_type}_{self.logfile}"
            if os.path.isfile(logfile):
                os.remove(logfile)
            result = json.loads(json.dumps(cloudinary.api.resources_by_moderation('perception_point', 'pending',
                                                                                  resource_type=resource_type)))
            data_list = result["resources"]  # data pulled from cloudinary api sits under the resources key as a list

            # if the asset list exists then pull the asset list read from it and make sure that the logs are not reported again
            if os.path.isfile(reported_asset_list):
                asset_list = []
                with open(reported_asset_list, "r") as reported_asset:
                    asset = reported_asset.readlines()
                for line in asset:
                    asset_list.append(line.replace("\n", ""))
                # print(asset_list)
                with open(logfile, 'x') as logs_file:
                    for data in data_list:
                        if data["asset_id"] not in asset_list:
                            with open(logfile, 'a') as write_file:
                                data['Log_type'] = 'Cloudninary'
                                json.dump(data, write_file)
                                write_file.write('\n')
                            with open(test_logfile, 'a') as write_file:
                                data['Log_type'] = 'Cloudninary'
                                json.dump(data, write_file)
                                write_file.write('\n')
                            with open(reported_asset_list, 'a') as write_file:
                                write_file.write(data["asset_id"] + "\n")
            else:
                # else condition to execute the logs for the first time in case the asset list does not exists
                with open(logfile, 'x') as logs_file:
                    with open(reported_asset_list, 'x') as reported_asset:
                        for data in data_list:
                            with open(logfile, 'a') as write_file:
                                data['Log_type'] = 'Cloudninary'
                                json.dump(data, logs_file)
                                write_file.write('\n')
                            with open(test_logfile, 'a') as write_file:
                                data['Log_type'] = 'Cloudninary'
                                json.dump(data, write_file)
                                write_file.write('\n')
                            with open(reported_asset_list, 'a') as write_file:
                                write_file.write(data["asset_id"] + "\n")


def main():
    lets_run_it = API_calls()
    lets_run_it.project_fall_back()
    lets_run_it.call_cloudinary()


main()
