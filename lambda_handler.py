import logging
from app import app


# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        logger.info(f"Event: {event}")

        # Add a check for warm-up events
        if 'warmup' in event and \
           event.get('source') == 'serverless-plugin-warmup':
            logger.info("WarmUp - Lambda is warm!")
            return {
                'statusCode': 200,
                'body': 'Warmed up!'
            }

        # Process the request through Chalice
        response = app(event, context)
        logger.info(f"Response: {response}")
        return response

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': 'Internal Server Error',
            'headers': {
                'Content-Type': 'application/json',
            }
        }
