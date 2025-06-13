from flask import Flask, jsonify
from CheckEmail import *


app = Flask(__name__)


@app.route('/check-and-reply', methods=['POST'])
def check_and_reply():
    try:
        email_ids, mail = check_emails()
        if email_ids:
            process_emails(email_ids, mail)
            message = f"Processed {len(email_ids)} new emails."
            status = "success"
        else:
            message = "No new emails found."
            status = "success"

        mail.close()
        mail.logout()

        # Only print when emails were processed
        if status == "success" and len(email_ids) > 0:
            print(f"✅ {message}")

        return jsonify({"status": status, "message": message})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
