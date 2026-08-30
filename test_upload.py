import urllib.request
import json
import time

url = 'http://127.0.0.1:5000/api/v1/documents/upload'
pdf_path = 'Decode_backend/backend/static/uploads/0c5a9677_DECODE_Test_Scientific_Charts.pdf'

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = []
body.append('--' + boundary)
body.append('Content-Disposition: form-data; name="file"; filename="DECODE_Test_Scientific_Charts.pdf"')
body.append('Content-Type: application/pdf')
body.append('')
with open(pdf_path, 'rb') as f:
    pdf_data = f.read()
    
body_str = '\r\n'.join(body) + '\r\n'
body_bytes = body_str.encode('utf-8') + pdf_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')

req = urllib.request.Request(url, data=body_bytes)
req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')

try:
    with urllib.request.urlopen(req) as resp:
        upload_resp = json.loads(resp.read().decode())
        doc_id = upload_resp.get('document_id') or upload_resp.get('id')
        print(f'Uploaded successfully, doc_id: {doc_id}')
        
        # Poll
        for _ in range(45):
            time.sleep(1)
            status_req = urllib.request.Request(f'http://127.0.0.1:5000/api/v1/documents/{doc_id}')
            with urllib.request.urlopen(status_req) as s_resp:
                s_data = json.loads(s_resp.read().decode())
                status = s_data.get('status', '').lower()
                print(f'Status: {status}')
                if status in ['complete', 'completed', 'done', 'success']:
                    break
                    
        # Fetch charts
        charts_req = urllib.request.Request(f'http://127.0.0.1:5000/api/v1/documents/{doc_id}/charts')
        with urllib.request.urlopen(charts_req) as c_resp:
            c_data = json.loads(c_resp.read().decode())
            print('\n--- CHART RESPONSE ---')
            print(json.dumps(c_data, indent=2)[:3000])
except Exception as e:
    print(f'Error: {e}')
