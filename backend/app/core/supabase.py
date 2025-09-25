from supabase import create_client, Client
from app.core.config import settings
from typing import Optional, Dict, Any, List, Union
import logging

logger = logging.getLogger(__name__)

class SupabaseClient:
    _instance = None
    
    def __init__(self):
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ValueError("Supabase URL and Key must be set in environment variables")
        
        try:
            self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            logger.info("Successfully initialized Supabase client")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    @classmethod
    def get_instance(cls) -> 'SupabaseClient':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def test_connection(self) -> bool:
        """Test the Supabase connection."""
        try:
            # A simple query to test the connection
            result = self.client.table('users').select('*').limit(1).execute()
            logger.info("Successfully connected to Supabase")
            return True
        except Exception as e:
            logger.error(f"Error connecting to Supabase: {e}")
            return False
    
    def query(self, table: str, action: str = 'select', query_params: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Generic query method for Supabase tables.
        
        Args:
            table: The name of the table to query
            action: The type of query to perform (select, insert, update, delete)
            query_params: A dictionary of query parameters
            **kwargs: Additional keyword arguments
            
        Returns:
            The result of the query
        """
        if query_params is None:
            query_params = {}
            
        try:
            query = self.client.table(table)
            
            # Handle different query actions
            if action == 'select':
                select_columns = query_params.get('select', '*')
                query = query.select(select_columns)
                
                # Add filters if provided
                if 'filters' in query_params:
                    for field, value in query_params['filters'].items():
                        query = query.eq(field, value)
                
                # Add pagination
                if 'range' in query_params:
                    start, end = query_params['range']
                    query = query.range(start, end)
                elif 'limit' in query_params:
                    query = query.limit(query_params['limit'])
                
                # Add ordering
                if 'order' in query_params:
                    column, desc = query_params['order']
                    query = query.order(column, desc=desc)
                
                result = query.execute()
                
            elif action == 'insert':
                if 'data' not in query_params:
                    raise ValueError("Missing 'data' in query_params for insert operation")
                result = query.insert(query_params['data']).execute()
                
            elif action == 'update':
                if 'data' not in query_params or 'id' not in query_params:
                    raise ValueError("Missing 'data' or 'id' in query_params for update operation")
                result = query.update(query_params['data']).eq('id', query_params['id']).execute()
                
            elif action == 'delete':
                if 'id' not in query_params:
                    raise ValueError("Missing 'id' in query_params for delete operation")
                result = query.delete().eq('id', query_params['id']).execute()
                
            else:
                raise ValueError(f"Unsupported query action: {action}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing {action} query on table {table}: {e}")
            raise

# Initialize the Supabase client
try:
    supabase = SupabaseClient.get_instance()
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    raise

def test_connection() -> bool:
    """Test the Supabase connection."""
    return supabase.test_connection()
