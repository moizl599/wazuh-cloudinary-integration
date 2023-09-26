import json
import os
from configparser import ConfigParser
import cloudinary.api

class API_calls:
    """
    A class to make API calls to Cloudinary.
    """

    def __init__(self, config_file: str):
        """
        Initializes the API_calls object with configurations from a file.
        
        :param config_file: Path to the configuration file containing necessary parameters.
        """
        # Loading configurations from the configuration file
        config = ConfigParser()
        config.read(config_file)
        
        # Assigning configurations to instance variables
        self.logfile = config.get('Cloudinary', 'logfile')
        self.reported_asset_list = config.get('Cloudinary', 'reported_asset_list')
        self.test_logfile = config.get('Cloudinary', 'test_logfile')
        self.resource_types = config.get('Cloudinary', 'resource_types').split(',')

    def project_fall_back(self):
        """
        Checks for the existence of the test logfile, creates it if not found.
        """
        if not os.path.isfile(self.test_logfile):
            with open(self.test_logfile, 'x') as f:
                print("All good now, pheww!")

    def call_cloudinary(self):
        """
        Calls the Cloudinary API to pull resources and logs the results.
        """
        for resource_type in self.resource_types:
            logfile = f"{self.logfile}_{resource_type}.log"
            # Removing the logfile to write new logs
            if os.path.isfile(logfile):
                os.remove(logfile)

            # Making an API call to Cloudinary
            result = cloudinary.api.resources_by_moderation('perception_point', 'pending', resource_type=resource_type)
            data_list = result["resources"]

            # Reading already reported assets from the file
            asset_list = []
            if os.path.isfile(self.reported_asset_list):
                with open(self.reported_asset_list, "r") as reported_asset:
                    asset_list = [line.strip() for line in reported_asset.readlines()]

            # Writing logs and updating the reported assets list
            with open(logfile, 'a') as logs_file, open(self.test_logfile, 'a') as test_file, open(self.reported_asset_list, 'a') as reported_asset:
                for data in data_list:
                    if data["asset_id"] not in asset_list:
                        data['Log_type'] = 'Cloudinary'
                        json.dump(data, logs_file)
                        logs_file.write('\n')
                        json.dump(data, test_file)
                        test_file.write('\n')
                        reported_asset.write(data["asset_id"] + "\n")


def main():
    """
    The main function to run the API calls and associated methods.
    """
    lets_run_it = API_calls('./key.cfg')
    lets_run_it.project_fall_back()
    lets_run_it.call_cloudinary()


if __name__ == "__main__":
    main()
