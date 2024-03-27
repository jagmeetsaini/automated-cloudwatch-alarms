from resources import Resources
from logger import configure_logger
from config import LOGS_LEVEL, STATISTIC_MAP, COMPARISON_OPERATOR_MAP, RESOURCE_DIMENSIONS_MAP, SNS_TOPIC_ARNS, MONITORING_METRIC_PREFIX, CUSTOM_MONITORING_METRIC_PREFIX, METRICS_VALIDATION_MAP

logger = configure_logger(file_name="utility.py", logs_level=LOGS_LEVEL)

class AlarmUtility:
    @staticmethod
    def get_dimensions(resource_arn, namespace):
        try:
            resource_arn = resource_arn
            namespace = namespace

            if namespace in ("AWS/EC2", "ElasticBeanstalk/CWAgent"):
                # Extract instance_id from resource_arn
                resource_id = resource_arn.split('/')[-1]

                # Fetch dimensions based on namespace
                dimensions = RESOURCE_DIMENSIONS_MAP.get(namespace, [])
                for dimension in dimensions:
                     if 'InstanceId' in dimension.values():
                        dimension['Value'] = resource_id

                return dimensions    
            
            if namespace in ("AWS/ElastiCache", "AWS/SQS", "AWS/RDS"):
                # Extract instance_id from resource_arn
                resource_id = resource_arn.split(':')[-1]

                # Fetch dimensions based on namespace
                dimensions = RESOURCE_DIMENSIONS_MAP.get(namespace, [])
                for dimension in dimensions:
                    dimension['Value'] = resource_id

                return dimensions

            if namespace == "AWS/ApplicationELB":
                # Extract instance_id from resource_arn
                resource_id = resource_arn.split(':')[-1].split("loadbalancer/")[-1]

                # Fetch dimensions based on namespace
                dimensions = RESOURCE_DIMENSIONS_MAP.get(namespace, [])
                for dimension in dimensions:
                    if 'LoadBalancer' in dimension.values():
                        dimension['Value'] = resource_id

                return dimensions        

            # If the namespace is not AWS/EC2 or doesn't have specific logic, return an empty list
            return []
        except Exception as e:
            logger.error(f"An error occurred in get_dimensions: {str(e)}")
            raise

    @staticmethod
    def create_alarm_name(resource_arn, namespace, metric_name):
        try:
            # Extract resource_identifier from resource_arn
            resource_identifier = resource_arn.split(':')[-1]

            return f"Automated Alarm | {namespace} | {resource_identifier} | {metric_name}"
        except Exception as e:
            logger.error(f"An error occurred in create_alarm_name: {str(e)}")
            raise

    @staticmethod
    def process_data(input_data):
        try:
            output_data = []
            for item in input_data:
                region = item['Region']
                resource_arn = item['ResourceARN']
                tags = item['Tags']
                namespace = tags.get('Enpass:Monitoring:Namespace', '')
                sns_topic_arn = tags.get('Enpass:Monitoring:SNSTopicARN', '')

                # Process standard or custom metric
                for key, value in tags.items():
                    if key.startswith(MONITORING_METRIC_PREFIX) or key.startswith(CUSTOM_MONITORING_METRIC_PREFIX):
                        metric_namespace = key.split(':')[-2] if key.startswith(CUSTOM_MONITORING_METRIC_PREFIX) else namespace
                        metric_info = value.split(':')
                        if len(metric_info) == 4:
                            statistic_code, comparison_operator_code, threshold, datapoints = metric_info
                            statistic = STATISTIC_MAP.get(statistic_code, 'NOT_FOUND')
                            comparison_operator = COMPARISON_OPERATOR_MAP.get(comparison_operator_code, 'NOT_FOUND')
                            output_data.append({
                                'Region': region,
                                'ResourceARN': resource_arn,
                                'Namespace': metric_namespace,
                                'SNSTopicARN': sns_topic_arn,
                                'AlarmMetrics': key.split(':')[-1],
                                'Statistic': statistic,
                                'ComparisonOperator': comparison_operator,
                                'Threshold': threshold,
                                'Datapoints': datapoints,
                                'Dimensions': AlarmUtility.get_dimensions(resource_arn=resource_arn, namespace=metric_namespace),
                                'AlarmName': AlarmUtility.create_alarm_name(resource_arn=resource_arn, namespace=namespace, metric_name=key.split(':')[-1])
                            })
            return output_data
        except Exception as e:
            logger.error(f"An error occurred in process_data: {str(e)}")
            raise

    @staticmethod
    def remove_failed_resources(successful_resources, failed_resources):
        try:
            return successful_resources - failed_resources
        except Exception as e:
            logger.error(f"An error occurred in remove_failed_resources: {str(e)}")
            raise

    @staticmethod
    def validate_alarm_data(alarm_data):
        try:
            logger.debug("Validating Alarm Data")
            
            required_keys = ["Region", "ResourceARN", "Namespace", "SNSTopicARN", "AlarmMetrics", "Statistic", "ComparisonOperator", "Threshold", "Datapoints", "Dimensions", "AlarmName"]

            # Check if all required keys are present
            if not all(key in alarm_data for key in required_keys):
                logger.error("Missing required keys.")
                return False

            # Check if no key has an empty value
            if any(value == '' for value in alarm_data.values()):
                logger.error("Empty value found for a key.")
                return False

            # Validate Namespace
            if alarm_data["Namespace"] not in RESOURCE_DIMENSIONS_MAP:
                logger.error("Invalid Namespace:", alarm_data["Namespace"])
                return False

            # Validate Metric
            # if not Resources.validate_alarm_metric(metric_name=alarm_data["AlarmMetrics"], namespace=alarm_data["Namespace"]):
            #     logger.error("Invalid Metric:", alarm_data["AlarmMetrics"])
            #     return False

            # Staticly Validate Metric
            if alarm_data["AlarmMetrics"] not in METRICS_VALIDATION_MAP.get(alarm_data["Namespace"], []):
                logger.error("Invalid Metric:", alarm_data["AlarmMetrics"])
                return False

            # Validate SNS Topic
            if alarm_data["SNSTopicARN"] not in SNS_TOPIC_ARNS:
                logger.error("Invalid SNS Topic:", alarm_data["SNSTopicARN"])
                return False

            # Validate Statistic
            if alarm_data["Statistic"] not in STATISTIC_MAP.values():
                logger.error("Invalid Statistic:", alarm_data["Statistic"])
                return False

            # Validate Comparison Operator
            if alarm_data["ComparisonOperator"] not in COMPARISON_OPERATOR_MAP.values():
                logger.error("Invalid Comparison Operator:", alarm_data["ComparisonOperator"])
                return False

            # Validate Datapoints
            try:
                datapoints = int(alarm_data["Datapoints"])
                if datapoints <= 0:
                    logger.error("Invalid Datapoints:", alarm_data["Datapoints"])
                    return False
            except ValueError:
                logger.error("Invalid Datapoints:", alarm_data["Datapoints"])
                return False

            # Validate Threshold
            try:
                threshold = float(alarm_data["Threshold"])
            except ValueError:
                logger.error("Invalid Threshold:", alarm_data["Threshold"])
                return False

            logger.debug("Alarm data is valid.")
            return True
        except Exception as e:
            logger.error(f"An error occurred in validate_alarm_data: {str(e)}")
            raise