"""
Admin Dashboard for College Chatbot
Flask web interface for monitoring analytics and system health
"""

from flask import Flask, render_template, jsonify, request
from app.services.analytics import AnalyticsSystem
import os

app = Flask(__name__, template_folder='templates')
analytics = AnalyticsSystem()


@app.route('/')
def dashboard():
    """Main dashboard page"""
    stats = analytics.get_stats(days=7)
    return render_template('dashboard.html', stats=stats)


@app.route('/api/stats')
def api_stats():
    """API endpoint for stats (for AJAX refresh)"""
    days = int(request.args.get('days', 7))
    stats = analytics.get_stats(days=days)
    return jsonify(stats)


@app.route('/queries')
def recent_queries():
    """Recent queries page"""
    queries = analytics.get_recent_queries(limit=100)
    return render_template('queries.html', queries=queries)


@app.route('/failed')
def failed_queries():
    """Failed queries page for debugging"""
    queries = analytics.get_failed_queries(limit=50)
    return render_template('failed.html', queries=queries)


if __name__ == '__main__':
    print("=" * 70)
    print("TKRCET Chatbot Admin Dashboard")
    print("=" * 70)
    print("\nStarting dashboard server...")
    print("Access dashboard at: http://localhost:5000")
    print("\nPages available:")
    print("  • Dashboard: http://localhost:5000/")
    print("  • Recent Queries: http://localhost:5000/queries")
    print("  • Failed Queries: http://localhost:5000/failed")
    print("\nPress Ctrl+C to stop")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)


@app.route('/')
def dashboard():
    """Main dashboard page"""
    stats = analytics.get_stats(days=7)
    return render_template('dashboard.html', stats=stats)


@app.route('/api/stats')
def api_stats():
    """API endpoint for stats (for AJAX refresh)"""
    days = int(request.args.get('days', 7))
    stats = analytics.get_stats(days=days)
    return jsonify(stats)


@app.route('/query', methods=['POST'])
def query():
    """Handle chat queries"""
    try:
        data = request.json
        message = data.get('message')
        session_id = data.get('session_id')
        language = data.get('language', 'en')
        
        if not message:
            return jsonify({'error': 'Message required'}), 400
            
        chatbot = get_agent()
        if not chatbot:
             return jsonify({'error': 'Chatbot system not initialized'}), 500
             
        # TODO: Pass session_id and language if supported by agent
        answer = chatbot(message)
        
        return jsonify({
            'answer': answer,
            'session_id': session_id or 'new_session' 
        })
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/queries')
def recent_queries():
    """Recent queries page"""
    queries = analytics.get_recent_queries(limit=100)
    return render_template('queries.html', queries=queries)


@app.route('/failed')
def failed_queries():
    """Failed queries page for debugging"""
    queries = analytics.get_failed_queries(limit=50)
    return render_template('failed.html', queries=queries)


if __name__ == '__main__':
    print("=" * 70)
    print("TKRCET Chatbot Admin Dashboard")
    print("=" * 70)
    print("\nStarting dashboard server...")
    print("Access dashboard at: http://localhost:8000")
    print("\nPages available:")
    print("  • Dashboard: http://localhost:8000/")
    print("  • Recent Queries: http://localhost:8000/queries")
    print("  • Failed Queries: http://localhost:8000/failed")
    print("\nPress Ctrl+C to stop")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=8000)
