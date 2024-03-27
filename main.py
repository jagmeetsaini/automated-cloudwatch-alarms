import concurrent.futures
import time
from logger import configure_logger
from resources import Resources
from utility import AlarmUtility
from alarms import Alarm
from config import *

logger = configure_logger(file_name="main.py", logs_level=LOGS_LEVEL)

def process_region(region):
    try:
        logger.debug(f"Fetching Resources for Region: {region}")
        resource = Resources()
        resources_data = resource.get_resources(region=region, tag_name=MONITORING_TAG_NAME, tag_value=MONITORING_TAG_VALUE, monitoring_tags_prefix=MONITORING_TAGS_PREFIX)
        return resources_data
    except Exception as e:
        logger.error(f"Error fetching resources for region {region}: {str(e)}")
        return []
    
# Define a function to validate alarm data
def validate_alarm(alarm_data):
    alarm_utility = AlarmUtility()

    if alarm_utility.validate_alarm_data(alarm_data=alarm_data):
        valid_alarms_data.append(alarm_data)
    else:
        FAILED_TO_CREATE_ALARM_RESOURCE_LIST.add(alarm_data["ResourceARN"])

def lambda_handler(event, context):
    try:
        logger.info("Lambda function execution started.")

        start_time = time.time()

        # Create an instance of the classes
        resource = Resources()
        alarm_utility = AlarmUtility()
        alarm = Alarm()

        
       # Fetch resources for each region in parallel
        logger.info("Fetching Resources Data") 
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(process_region, regions)

        # Flatten the list of lists
        resources_data = [item for sublist in results for item in sublist if item]
        logger.info("Resources data fetched successfully")

        logger.debug("Resources Fetched:")
        logger.debug(resources_data)
        logger.debug(" ")
        
        logger.info("Processing Resources Data") 
        alarms_data = alarm_utility.process_data(resources_data)
        logger.info("Done Processing Resources Data") 

        logger.debug("Processed alarms data:")
        logger.debug(alarms_data)
        logger.debug(" ")

        if alarms_data:
            logger.info("Validating Alarms Data")
            # Submit validation tasks to ThreadPoolExecutor
            with concurrent.futures.ThreadPoolExecutor() as executor:
                validation_futures = [executor.submit(validate_alarm, alarm_data) for alarm_data in alarms_data]
            logger.info("Done Validating Alarms Data")

            logger.info("Setting Alarms on Resources")
            with concurrent.futures.ThreadPoolExecutor(max_workers=SET_ALARMS_WORKER) as executor:
                for alarm_data in valid_alarms_data:
                    executor.submit(alarm.set_alarm, alarm_config=alarm_data)
            logger.info("Done Setting Alarms on Resources")

            NEW_SUCCESSFULL_TO_CREATE_ALARM_RESOURCE_LIST = alarm_utility.remove_failed_resources(successful_resources=SUCCESSFULL_TO_CREATE_ALARM_RESOURCE_LIST, 
                                                                                                failed_resources=FAILED_TO_CREATE_ALARM_RESOURCE_LIST)
            
            if NEW_SUCCESSFULL_TO_CREATE_ALARM_RESOURCE_LIST:
                resource.modify_tag_value(resources_arns=NEW_SUCCESSFULL_TO_CREATE_ALARM_RESOURCE_LIST, tag_key=MONITORING_TAG_NAME, new_value=SUCCESSFULL_MONITORING_TAG_VALUE)
                logger.info("Updated 'Enpass:Monitoring:Enabled' Tag value from '1' --> '2' for successful resources")

                if FAILED_TO_CREATE_ALARM_RESOURCE_LIST:
                    resource.modify_tag_value(resources_arns=FAILED_TO_CREATE_ALARM_RESOURCE_LIST, tag_key=MONITORING_TAG_NAME, new_value=FAILED_MONITORING_TAG_VALUE)
                    logger.info("Updated 'Enpass:Monitoring:Enabled' Tag value from '1' --> '3' for failed resources")

            # Calculate resource counts
            total_resources = len(NEW_SUCCESSFULL_TO_CREATE_ALARM_RESOURCE_LIST) + len(FAILED_TO_CREATE_ALARM_RESOURCE_LIST)
            total_successful_resources = len(NEW_SUCCESSFULL_TO_CREATE_ALARM_RESOURCE_LIST)
            total_failed_resources = len(FAILED_TO_CREATE_ALARM_RESOURCE_LIST)

            # Log lists of successful and failed resources
            logger.debug("Successful resources list:")
            logger.debug(NEW_SUCCESSFULL_TO_CREATE_ALARM_RESOURCE_LIST)
            logger.debug("Failed resources list:")
            logger.debug(FAILED_TO_CREATE_ALARM_RESOURCE_LIST)
            logger.info(f"TOTAL: {total_resources} | SUCCESS: {total_successful_resources} | FALIED: {total_failed_resources}")
        else:
            logger.info("No Alarms Found to Set")

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info("Execution Completed")
        logger.info(f"Total Execution Time: {execution_time} seconds")

        return {
            'statusCode': 200,
            'body': 'Program Executed'
        }
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': 'An error occurred during execution.'
        }

# Invoke the lambda_handler function
lambda_handler(event=0, context=0)