# app.py - Shopify webhook receiver + watermark-removal pipeline (placeholder)
import os
import logging
from flask import Flask, request, jsonify, abort
import requests
from werkzeug.utils import secure_filename
from watermark import remove_watermark
from klaviyo_notify import send_klaviyo_image_email

SHOPIFY_SHARED_SECRET = os.getenv('SHOPIFY_SECRET', '')
KLAVIYO_API_KEY = os.getenv('KLAVIYO_API_KEY', '')
SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL', 'support@yourdomain.com')

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def verify_shopify_webhook(req):
    # TODO: implement HMAC verification using SHOPIFY_SHARED_SECRET in production
    return True

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/webhook/shopify', methods=['POST'])
def shopify_webhook():
    if not verify_shopify_webhook(request):
        abort(401)
    data = request.get_json(silent=True)
    if not data:
        app.logger.error('No JSON received')
        return jsonify({'ok': False, 'reason': 'no json'}), 400

    image_url = None
    for item in data.get('note_attributes', []):
        name = item.get('name','').lower()
        if 'image' in name or 'photo' in name or 'upload' in name:
            image_url = item.get('value')
    if not image_url:
        for li in data.get('line_items', []):
            for prop in li.get('properties', []):
                if isinstance(prop, dict):
                    name = prop.get('name','').lower()
                    if 'image' in name or 'photo' in name or 'upload' in name:
                        image_url = prop.get('value')
    if not image_url:
        for k in ('image','photo','uploaded_image','upload'):
            if k in data:
                image_url = data.get(k)

    if not image_url:
        app.logger.info('No image URL found in payload; returning success to stop retries.')
        return jsonify({'ok': True, 'message': 'no image url found'}), 200

    try:
        filename = secure_filename(image_url.split('?')[0].split('/')[-1])
        local_in = os.path.join(UPLOAD_FOLDER, filename)
        local_out = os.path.join(OUTPUT_FOLDER, f'clean_{filename}')

        app.logger.info(f'Downloading image: {image_url}')
        r = requests.get(image_url, timeout=30)
        r.raise_for_status()
        with open(local_in, 'wb') as f:
            f.write(r.content)

        app.logger.info('Running watermark removal (placeholder)...')
        ok = remove_watermark(local_in, local_out)
        if not ok:
            app.logger.error('remove_watermark returned False')
            return jsonify({'ok': False, 'reason': 'watermark removal failed'}), 500

        customer_email = data.get('email') or data.get('contact_email') or (data.get('billing_address') or {}).get('email')
        if customer_email:
            app.logger.info(f'Sending cleaned image to {customer_email}')
            try:
                send_klaviyo_image_email(customer_email, local_out, KLAVIYO_API_KEY)
            except Exception as e:
                app.logger.error(f'Failed to send Klaviyo email: {e}')

        return jsonify({'ok': True, 'clean_image': local_out}), 200
    except Exception as e:
        app.logger.exception('Error processing webhook')
        return jsonify({'ok': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
