"""
Diagnostic endpoint to find import errors
"""
import json
import traceback
import sys

def handler(event, context=None):
    """Diagnostic handler to test imports"""
    results = {}
    
    # Test 1: Basic Python
    results['python_version'] = sys.version
    results['python_path'] = sys.path[:3]
    
    # Test 2: Try importing config
    try:
        from config import settings
        results['config'] = 'OK'
        results['supabase_url_exists'] = bool(getattr(settings, 'supabase_url', None))
    except Exception as e:
        results['config'] = f'ERROR: {str(e)}'
        results['config_trace'] = traceback.format_exc()
    
    # Test 3: Try importing supabase_client
    try:
        from supabase_client import supabase
        results['supabase_client'] = 'OK'
    except Exception as e:
        results['supabase_client'] = f'ERROR: {str(e)}'
        results['supabase_trace'] = traceback.format_exc()
    
    # Test 4: Try importing auth_service_supabase
    try:
        from auth_service_supabase import create_user
        results['auth_service_supabase'] = 'OK'
    except Exception as e:
        results['auth_service_supabase'] = f'ERROR: {str(e)}'
        results['auth_trace'] = traceback.format_exc()
    
    # Test 5: Try importing main
    try:
        from main import app
        results['main'] = 'OK'
    except Exception as e:
        results['main'] = f'ERROR: {str(e)}'
        results['main_trace'] = traceback.format_exc()
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(results, indent=2)
    }

