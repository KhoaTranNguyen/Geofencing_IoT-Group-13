import azure.functions as func
import json

def main(req: func.HttpRequest, connectionInfo) -> func.HttpResponse:
    # Handle OPTIONS preflight for CORS
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Max-Age": "86400"
            }
        )

    # Return SignalR info with CORS header
    return func.HttpResponse(
        body=json.dumps(connectionInfo),
        mimetype="application/json",
        headers={
            "Access-Control-Allow-Origin": "*"
        }
    )