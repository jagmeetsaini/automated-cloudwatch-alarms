import boto3
from logger import configure_logger
from config import LOGS_LEVEL

logger = configure_logger(file_name="resources.py", logs_level=LOGS_LEVEL)

class Resources:
    def __init__(self):
        self.tag_client = boto3.client('resourcegroupstaggingapi')

    def get_resources(self, region=None, tag_name=None, tag_value=None, monitoring_tags_prefix=None):
        try:
            resources = []
            regions = [region] if region else [reg['RegionName'] for reg in self.tag_client.describe_regions()['Regions']]

            for reg in regions:
                paginator = self.tag_client.get_paginator('get_resources')
                tag_filters = [{'Key': tag_name}] if tag_name else []
                if tag_value:
                    tag_filters[0]['Values'] = [tag_value]

                for page in paginator.paginate(TagFilters=tag_filters, ResourcesPerPage=100):
                    for resource in page['ResourceTagMappingList']:
                        resource_arn = resource['ResourceARN']
                        tags = resource.get('Tags', {})
                        if isinstance(tags, list):  # Ensure tags is always a dictionary
                            tags = {item['Key']: item['Value'] for item in tags}
                        if monitoring_tags_prefix:
                            tags = {key: value for key, value in tags.items() if key.startswith(monitoring_tags_prefix)}
                        resources.append({'Region': reg, 'ResourceARN': resource_arn, 'Tags': tags})
            return resources
        except Exception as e:
            logger.error(f"Error fetching resources: {e}")
            return []

    def modify_tag_value(self, resources_arns, tag_key, new_value):
        try:
            resources_arns = list(resources_arns)
            # Split resources_arns into chunks of 20
            chunks = [resources_arns[i:i + 20] for i in range(0, len(resources_arns), 20)]

            for chunk in chunks:
                # Delete the existing tag
                response_delete = self.tag_client.untag_resources(
                    ResourceARNList=chunk,
                    TagKeys=[tag_key]
                )
                logger.debug(f"Delete Tag Response: {response_delete}")
                # Create a new tag with the updated value
                response_create = self.tag_client.tag_resources(
                    ResourceARNList=chunk,
                    Tags={tag_key: new_value}
                )
                logger.debug(f"Create Tag Response: {response_create}")

            return True
        except Exception as e:
            logger.error(f"Error modifying tag value: {e}")
            return False
        
    def validate_alarm_metric(metric_name, namespace):
        try:
            cloudwatch_client = boto3.client('cloudwatch')
            response = cloudwatch_client.list_metrics(
                MetricName=metric_name,
                Namespace=namespace
            )
            metrics = response['Metrics']
            if metrics:
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error validating alarm metric: {e}")
            return False
