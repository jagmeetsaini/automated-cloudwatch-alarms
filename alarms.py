import boto3
from logger import configure_logger
from resources import Resources
from config import LOGS_LEVEL, SUCCESSFULL_TO_CREATE_ALARM_RESOURCE_LIST, FAILED_TO_CREATE_ALARM_RESOURCE_LIST, ALARM_PERIOD

logger = configure_logger(file_name="alarms.py", logs_level=LOGS_LEVEL)

class Alarm:
    def __init__(self):
        self.cloudwatch_client = boto3.client('cloudwatch')
        # Create an instance of the Resources class
        self.resource = Resources()

    def set_alarm(self, alarm_config):
        try:
            response = self.cloudwatch_client.put_metric_alarm(
                AlarmName=alarm_config['AlarmName'],
                AlarmDescription=f"This is a lambda generated alarm for {alarm_config['AlarmMetrics']}",
                Namespace=alarm_config['Namespace'],
                MetricName=alarm_config['AlarmMetrics'],
                Dimensions=alarm_config['Dimensions'],
                Threshold=float(alarm_config['Threshold']),
                ComparisonOperator=alarm_config['ComparisonOperator'],
                Statistic=alarm_config['Statistic'],
                AlarmActions=[alarm_config['SNSTopicARN']],

                EvaluationPeriods=int(alarm_config['Datapoints']),
                DatapointsToAlarm=int(alarm_config['Datapoints']),
                Period=ALARM_PERIOD,

                ActionsEnabled=True,
                TreatMissingData='missing',

                Tags=[{'Key': 'Purpose', 'Value': 'Automated Cloudwatch Alarm'}])

            # Adding the Resource ARN to SUCCESSFULL_TO_CREATE_ALARM_RESOURCE_LIST
            SUCCESSFULL_TO_CREATE_ALARM_RESOURCE_LIST.add(alarm_config["ResourceARN"])
            
            logger.debug("Alarm successfully set: %s", response)
            logger.debug("")
            return "Success"
        except Exception as e:
            FAILED_TO_CREATE_ALARM_RESOURCE_LIST.add(alarm_config["ResourceARN"])
            logger.error("Error setting alarm: %s", e)
            return "Error"
