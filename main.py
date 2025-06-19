from flask import Flask, render_template_string, request, send_file
import requests
import pandas as pd
import io

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KeepaKırbaç™ V2</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-dark text-white">
    <div class="container py-5">
        <h1 class="text-center mb-4">🔥 KeepaZonify™ V2 - ASIN Toplama Paneli</h1>
        <form method="post">
            <div class="mb-3">
                <label for="api_key" class="form-label">Keepa API Key</label>
                <input type="text" class="form-control" id="api_key" name="api_key" required>
            </div>
            <div class="mb-3">
                <label for="category_id" class="form-label">Kategori ID (örnek: 1055398)</label>
                <input type="text" class="form-control" id="category_id" name="category_id" required>
            </div>
            <button type="submit" class="btn btn-danger w-100">💥 ASIN'leri Tokatla</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        api_key = request.form['api_key']
        category_id = request.form['category_id']

        url = f"https://api.keepa.com/bestsellers?key={api_key}&domain=1&category={category_id}"
        response = requests.get(url)

        if response.status_code != 200:
            return f"Hata: Keepa API isteği başarısız oldu. Kod: {response.status_code}"

        data = response.json()

        asin_list = []

        if 'bestSellersList' in data and 'asinList' in data['bestSellersList']:
            asin_list = data['bestSellersList']['asinList']
        else:
            return "Keepa API yanıtında asinList bulunamadı."

        if not asin_list:
            return "Bu kategori için ASIN verisi bulunamadı."

        df = pd.DataFrame(asin_list, columns=['ASIN'])
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        return send_file(
            io.BytesIO(output.read().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'keepa_asin_list_category_{category_id}.csv'
        )

    return render_template_string(HTML_TEMPLATE)
