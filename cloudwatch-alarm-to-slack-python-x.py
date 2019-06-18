import boto3
import json
import logging
import os

from base64 import b64decode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

SLACK_CHANNEL = os.environ['slackChannel']

HOOK_URL = "https://" + os.environ['HookUrl']

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Event: " + str(event))

    message = json.loads(event['Records'][0]['Sns']['Message'])
    
    logger.info("Message: " + str(message))
    #printf(message)

    alarm_name = message['AlarmName']
    new_state = message['NewStateValue']
    reason = message['NewStateReason']
    statetime = message['StateChangeTime']
    trigger = message['Trigger']
    metricname = message['Trigger']['MetricName']
    description = message['AlarmDescription']


    color = 'good'
    if new_state != 'OK':
        color = 'danger'


    slack_message = {
        'channel': SLACK_CHANNEL,
        'username': "aws_cloudwatch2lambda",
        'icon_emoji': ":aws-cloudwatch:",
        'attachments': [
            {
                'color': color,
                'text': "Date: *%s* \n MetricName: *%s* \n AlarmDescription: *%s* \n *%s* *state is now* *%s*\n %s\n" % (statetime, metricname, description, alarm_name, new_state, reason)
            }
        ]
    }

    req = Request(HOOK_URL, json.dumps(slack_message).encode('utf-8'))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)

