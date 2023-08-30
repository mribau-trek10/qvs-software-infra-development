import boto3
import json
import requests

print('Loading function')
dynamodb = boto3.resource('dynamodb')



def lambda_handler(event, context):
    evt_str = json.dumps(event)

    print(f'event is: {evt_str}')

    body = json.loads(event["body"])

    store_id = body["storeId"]

    print(f'Request is for store ID {store_id}')

    endpoints_table = dynamodb.Table('Endpoints')  # Use the correct table name here

    endpoint_data = endpoints_table.get_item(
        Key={
            'storeid': store_id
        }
    )

    if "Item" not in endpoint_data:
        rc = {
            'statusCode': 400,
            'body': f'Store ID {store_id} not found',
            'headers': {
                'Content-Type': 'application/json',
            }
        }
    else:
        try:
            endpoint = endpoint_data["Item"]["endpoint"]

            url = endpoint + event["path"]

            print(f'Endpoint is {url}')

            headers = {
                "accept": "application/json",
                "Content-Type": "application/json"
            }

            response = requests.post(url, data=json.dumps(body), headers=headers)

            rc = {
                'statusCode': response.status_code,
                'body': response.text,
                'headers': {
                    'Content-Type': 'application/json',
                },
            }
        except Exception as e:
            rc = {
                'statusCode': 502,
                'body': str(e),
                'headers': {
                    'Content-Type': 'application/json',
                },
            }

    print('rc ' + json.dumps(rc))

    return rc


if __name__ == "__main__":
    event_str = """
    {

        "resource": "/v1/order/product",

        "path": "/v1/order/product",

        "httpMethod": "POST",

        "headers": null,

        "multiValueHeaders": null,

        "queryStringParameters": null,

        "multiValueQueryStringParameters": null,

        "pathParameters": null,

        "stageVariables": null,

        "requestContext": {

            "resourceId": "fszzxw",

            "resourcePath": "/v1/order/product",

            "operationName": "GetProduct",

            "httpMethod": "POST",

            "extendedRequestId": "IKtE9GJGCYcFYWA=",

            "requestTime": "16/Jul/2023:17:27:33 +0000",

            "path": "/v1/order/product",

            "accountId": "897716045651",

            "protocol": "HTTP/1.1",

            "stage": "test-invoke-stage",

            "domainPrefix": "testPrefix",

            "requestTimeEpoch": 1689528453829,

            "requestId": "97e5dccc-7f6e-4b4c-a3dc-e6fed62e5b0d",

            "identity": {

                "cognitoIdentityPoolId": null,

                "cognitoIdentityId": null,

                "apiKey": "test-invoke-api-key",

                "principalOrgId": null,

                "cognitoAuthenticationType": null,

                "userArn": "arn:aws:iam::897716045651:user/john.foley",

                "apiKeyId": "test-invoke-api-key-id",

                "userAgent": "aws-cli/2.12.6 Python/3.11.4 Windows/10 exe/AMD64 prompt/off command/apigateway.test-invoke-method",

                "accountId": "897716045651",

                "caller": "AIDAIDUJKHHXLXLTMZ5GS",

                "sourceIp": "test-invoke-source-ip",

                "accessKey": "AKIA5CBALY5J23UP5KUA",

                "cognitoAuthenticationProvider": null,

                "user": "AIDAIDUJKHHXLXLTMZ5GS"

            },

            "domainName": "testPrefix.testDomainName",

            "apiId": "yp7yfp4e34"

        },

        "isBase64Encoded": false

    }
    """

    call_data_str = """
    {
        "cartItem": {
                "externalIdentifiers": [],
                "id": "1037416846",
                "lineItemId": "CARTITEM-001",
                "quantity": {
                        "unit": "unit",
                        "value": "1"
                },
                "type": "SCANCODE"
        },
        "shopperIdentity": {
                "id": "TonyHicks"
        },
        "shoppingTripId": "ACH-123456",
        "storeId": "100"
    }
    """

    evt = json.loads(event_str)

    call_data = json.loads(call_data_str)
    evt["body"] = json.dumps(call_data)

    lambda_handler(evt, None)
    # print(event)
