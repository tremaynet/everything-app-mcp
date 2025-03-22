import json
import boto3
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Example file with intentional errors for demonstration
# This would be a Lambda function for processing user data streams

class DataProcessor:
    def __init__(self, kinesis_stream_name: str, dynamodb_table: str):
        self.kinesis_client = boto3.client('kinesis')
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(dynamodb_table)
        self.stream_name = kinesis_stream_name
        
    def process_data_stream(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming data from a Kinesis stream
        
        Args:
            event: Lambda event containing Kinesis records
            
        Returns:
            Processing statistics
        """
        # Intentional type error - records should be accessed with ['Records']
        records = event.Records
        
        processed_count = 0
        for record in records:
            # Decode and parse the Kinesis data
            payload = json.loads(record['kinesis']['data'])
            
            # INTENTIONAL ERROR: Missing await for async function
            result = self._process_payload(payload)
            
            processed_count += 1
        
        # Return processing statistics
        return {
            'processed_records': processed_count,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _process_payload(self, payload: Dict[str, Any]) -> bool:
        """Process a single data payload
        
        Args:
            payload: The data payload to process
            
        Returns:
            Success indicator
        """
        user_id = payload.get('user_id')
        if not user_id:
            # INTENTIONAL ERROR: Undefined variable
            logging.error("Missing user_id in payload")
            return False
        
        # Store processed data in DynamoDB
        try:
            self.table.put_item(Item={
                'user_id': user_id,
                'timestamp': payload.get('timestamp'),
                'data_type': payload.get('data_type'),
                'metrics': payload.get('metrics', {}),
                'processed_at': datetime.now().isoformat()
            })
            return True
        except Exception as e:
            # INTENTIONAL ERROR: f-string syntax error
            print(f"Error storing data: {e}")
            return False

# Lambda handler function
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda entry point
    
    Args:
        event: The event dict from AWS Lambda
        context: The context object from AWS Lambda
        
    Returns:
        Processing results
    """
    processor = DataProcessor(
        kinesis_stream_name=os.environ['KINESIS_STREAM'],
        dynamodb_table=os.environ['DYNAMODB_TABLE']
    )
    
    return processor.process_data_stream(event)