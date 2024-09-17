from flask import Flask, request, jsonify
import smtplib
import dns.resolver
import socket
import time

app = Flask(__name__)

# Address used for SMTP MAIL FROM command.
FROM_ADDRESS = 'soaanxr@yopmail.com'

def verify_email(address_to_verify):
    # Get domain for DNS lookup
    split_address = address_to_verify.split('@')
    domain = str(split_address[1])

    try:
        # MX record lookup
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = records[0].exchange
        mx_record = str(mx_record)

        # Set a timeout for the SMTP connection
        socket.setdefaulttimeout(10)  # 10 seconds timeout

        # SMTP lib setup
        server = smtplib.SMTP()
        server.set_debuglevel(0)

        # SMTP Conversation with timeout handling
        start_time = time.time()
        try:
            server.connect(mx_record)
            server.helo()  # Get local server hostname
            server.mail(FROM_ADDRESS)
            code, message = server.rcpt(address_to_verify)
        except (socket.timeout, socket.error) as e:
            print(e)
            code = 408  # Custom code for timeout/error
        finally:
            server.quit()

        elapsed_time = time.time() - start_time

    except Exception as e:
        code = 400

    return code

@app.route('/verify-email', methods=['POST'])
def verify_email_endpoint():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    code = verify_email(email)

    if code == 250:
        return jsonify({'status': 'success', 'message': 'Email is valid'}), 200
    elif code == 408:
        return jsonify({'status': 'timeout', 'message': 'SMTP timeout or connection error'}), 408
    else:
        return jsonify({'status': 'bad', 'message': 'Invalid email address'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
