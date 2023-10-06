from flask import Flask, jsonify, request
admission_controller = Flask(__name__)

@admission_controller.route('/validate/deployments', methods=['POST'])
def deployment_webhook():
    request_info = request.get_json()
    if request_info["request"]["object"]["metadata"]["labels"].get("allow"):
        return admission_response(True, "Allow label exists")
    return admission_response(False, "Not allowed without allow label")
    
def admission_response(allowed, message):
    return jsonify({"response": {"allowed": allowed, "status": {"message": message}}})
if __name__ == '__main__':
    admission_controller.run(host='0.0.0.0', port='8001', ssl_context=("/app/tls.crt", "/app/tls.key"))
