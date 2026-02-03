"""Simple Flask server for SAM.gov export UI."""

import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, Response
from dotenv import load_dotenv

from .client import SamGovClient
from .exporter import export_to_csv_string

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')

# Store results in memory for download
_last_export = {'csv_data': None, 'filename': None, 'count': 0}


@app.route('/')
def index():
    """Render the main UI."""
    return render_template('index.html')


@app.route('/api/search', methods=['POST'])
def search():
    """Search SAM.gov and export to CSV."""
    global _last_export

    data = request.json
    naics = data.get('naics', '').strip() or None  # Empty string = all
    days = int(data.get('days', 30))

    # Validate
    if days < 1 or days > 365:
        return jsonify({'error': 'Days must be between 1 and 365'}), 400

    date_to = datetime.now()
    date_from = date_to - timedelta(days=days)

    try:
        client = SamGovClient()
        opportunities = client.search_opportunities(
            naics_code=naics,
            posted_from=date_from,
            posted_to=date_to,
        )

        if not opportunities:
            return jsonify({
                'success': True,
                'count': 0,
                'message': 'No opportunities found matching criteria',
                'naics': naics or 'all',
                'date_from': date_from.strftime('%Y-%m-%d'),
                'date_to': date_to.strftime('%Y-%m-%d'),
            })

        # Export to CSV in memory
        naics_label = naics or 'all'
        filename = f'sam_export_{naics_label}_{date_from.strftime("%Y%m%d")}_{date_to.strftime("%Y%m%d")}.csv'
        csv_data = export_to_csv_string(opportunities)

        _last_export = {
            'csv_data': csv_data,
            'filename': filename,
            'count': len(opportunities)
        }

        # Return sample data for preview
        sample = []
        for opp in opportunities[:10]:
            sample.append({
                'noticeId': opp.get('noticeId', ''),
                'title': opp.get('title', '')[:80],
                'naicsCode': opp.get('naicsCode', ''),
                'postedDate': opp.get('postedDate', ''),
                'type': opp.get('type', ''),
            })

        return jsonify({
            'success': True,
            'count': len(opportunities),
            'sample': sample,
            'filename': filename,
            'naics': naics or 'all',
            'date_from': date_from.strftime('%Y-%m-%d'),
            'date_to': date_to.strftime('%Y-%m-%d'),
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500


@app.route('/api/download')
def download():
    """Download the last exported CSV."""
    if not _last_export['csv_data']:
        return jsonify({'error': 'No export available. Please run a search first.'}), 404

    return Response(
        _last_export['csv_data'],
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={_last_export["filename"]}'
        }
    )


def run_server(host='127.0.0.1', port=5050, debug=True):
    """Run the Flask development server."""
    print(f"\n  SAM.gov Export Tool")
    print(f"  Open http://{host}:{port} in your browser\n")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_server()
