"""Simple webhook receiver using Flask."""
from flask import Flask, request, jsonify


def create_app(handler=None):
    app = Flask(__name__)

    @app.route("/webhook", methods=["POST"])
    def webhook():
        payload = request.get_json(silent=True) or {}
        headers = dict(request.headers)
        if handler:
            handler(payload, headers)
        return jsonify({"status": "received"}), 200

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)