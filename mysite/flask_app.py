from flask import Flask, request, jsonify

app = Flask(__name__)

# Existing route
@app.route('/')
def hello_world():
    return 'Hello from Flask!'

# Updated route to match the URL path: /hangar/submit-payroll-mandate
@app.route('/hangar/submit-payroll-mandate', methods=['POST'])
def submit_payroll_mandate():
    # You can access data sent in the request here
    data = request.get_json()
    
    # Placeholder for your payroll logic
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    print(f"Received payroll mandate: {data}")
    
    return jsonify({"message": "Payroll mandate received successfully!"}), 200

if __name__ == '__main__':
    app.run(debug=True)