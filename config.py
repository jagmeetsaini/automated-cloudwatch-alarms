LOGS_LEVEL = "INFO" ##'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'
regions=["us-west-2"]

SET_ALARMS_WORKER = 1

MONITORING_TAGS_PREFIX = "Enpass:Monitoring:"
MONITORING_TAG_NAME = "Enpass:Monitoring:Enabled"
MONITORING_TAG_VALUE = "1"

MONITORING_METRIC_PREFIX= "Enpass:Monitoring:Metric:"
CUSTOM_MONITORING_METRIC_PREFIX = "Enpass:Monitoring:CustomMetric:"

SUCCESSFULL_MONITORING_TAG_VALUE = "2"
FAILED_MONITORING_TAG_VALUE = "3"

SNS_TOPIC_ARNS = ["arn:aws:sns:us-west-2:712231853444:CloudWatch-Alarms-Notification-Topic"]
ALARM_PERIOD = 300

STATISTIC_MAP = {
    "SC": "SampleCount",
    "AVG": "Average",
    "SUM": "Sum",
    "MIN": "Minimum",
    "MAX": "Maximum"
}

COMPARISON_OPERATOR_MAP = {
    "GTET": "GreaterThanOrEqualToThreshold",
    "GTT": "GreaterThanThreshold",
    "LTT": "LessThanThreshold",
    "LTET": "LessThanOrEqualToThreshold"
}

METRICS_VALIDATION_MAP = {
        "AWS/ApplicationELB": ["TargetResponseTime", "HTTPCode_ELB_5XX_Count"],
        "AWS/EC2": ["CPUUtilization"],
        "ElasticBeanstalk/CWAgent": ["mem_used_percent"],
        "AWS/SQS": ["ApproximateNumberOfMessagesDelayed", "ApproximateAgeOfOldestMessage", "NumberOfEmptyReceives"],
        "AWS/ElastiCache": ["CPUUtilization", "EngineCPUUtilization", "DatabaseMemoryUsagePercentage", "FreeableMemory", "SwapUsage"],
        "AWS/RDS": ["CPUUtilization", "DatabaseConnections", "FreeableMemory", "FreeStorageSpace"]
    }

RESOURCE_DIMENSIONS_MAP = {
    "AWS/EC2": [
      {
         "Name":"InstanceId",
         "Value":"{{instance_id_value}}"
      }
   ],
   "ElasticBeanstalk/CWAgent": [
      {
         "Name":"InstanceId",
         "Value":"{{instance_id_value}}"
      }
   ],
   "AWS/SQS": [
       {
         "Name":"QueueName",
         "Value":"{{queue_name_value}}"
      }
   ],
   "AWS/RDS": [
       {
         "Name":"DBInstanceIdentifier",
         "Value":"{{db_instance_identifier_value}}"
      }
   ],
   "AWS/ElastiCache": [
       {
         "Name":"CacheClusterId",
         "Value":"{{cache_cluster_id_value}"
      }
   ],
   "AWS/ApplicationELB": [
       {
           "Name": "LoadBalancer",
           "Value": "{{load_balance_value}}"
       }
   ]
}


valid_alarms_data = []
SUCCESSFULL_TO_CREATE_ALARM_RESOURCE_LIST = set()
FAILED_TO_CREATE_ALARM_RESOURCE_LIST = set()