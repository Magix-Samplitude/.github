#!/usr/bin/env python3
import random
import time
import json
import threading
import queue
from collections import defaultdict
from datetime import datetime, timedelta

class DatabaseEmulator:
    def __init__(self):
        self.tables = {}
        self.indexes = {}
        self.transactions = []
        self.connections = []
        self.query_queue = queue.Queue()
        self.lock = threading.Lock()
        self.running = True
        
        self.initialize_schema()
        
    def initialize_schema(self):
        tables = {
            'users': ['id', 'username', 'email', 'created_at', 'last_login', 'status'],
            'repositories': ['id', 'name', 'owner_id', 'private', 'created_at', 'updated_at'],
            'commits': ['id', 'repo_id', 'author_id', 'message', 'hash', 'timestamp'],
            'issues': ['id', 'repo_id', 'title', 'status', 'created_by', 'assigned_to'],
            'pull_requests': ['id', 'repo_id', 'from_branch', 'to_branch', 'status'],
            'comments': ['id', 'issue_id', 'user_id', 'content', 'created_at'],
            'stars': ['user_id', 'repo_id', 'created_at'],
            'followers': ['user_id', 'follower_id', 'created_at']
        }
        
        for table_name, columns in tables.items():
            self.tables[table_name] = {
                'columns': columns,
                'rows': [],
                'row_count': 0,
                'created_at': datetime.now().isoformat()
            }
            
        self.create_indexes()
        
    def create_indexes(self):
        for table_name in self.tables:
            for column in self.tables[table_name]['columns'][:2]:
                index_name = f"idx_{table_name}_{column}"
                self.indexes[index_name] = {
                    'table': table_name,
                    'column': column,
                    'unique': random.choice([True, False]),
                    'cardinality': random.randint(100, 10000)
                }
    
    def generate_row(self, table_name):
        table = self.tables[table_name]
        row = {}
        
        for column in table['columns']:
            if column.endswith('_id') or column == 'id':
                row[column] = random.randint(1, 1000000)
            elif 'name' in column or 'title' in column:
                row[column] = f"{column}_{random.randint(1, 1000)}"
            elif column in ['email']:
                row[column] = f"user{random.randint(1, 1000)}@example.com"
            elif column in ['private', 'status']:
                row[column] = random.choice([True, False]) if column == 'private' else random.choice(['open', 'closed', 'merged'])
            elif 'at' in column or 'timestamp' in column:
                row[column] = (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat()
            elif column == 'message' or column == 'content':
                row[column] = f"Sample content {random.randint(1, 1000)}"
            else:
                row[column] = f"value_{random.randint(1, 100)}"
                
        return row
    
    def populate_table(self, table_name, rows=1000):
        table = self.tables[table_name]
        for _ in range(rows):
            row = self.generate_row(table_name)
            with self.lock:
                table['rows'].append(row)
                table['row_count'] += 1
    
    def simulate_query(self, table_name):
        operations = ['SELECT', 'INSERT', 'UPDATE', 'DELETE']
        weights = [0.7, 0.15, 0.1, 0.05]
        operation = random.choices(operations, weights=weights)[0]
        
        start_time = time.time()
        
        if operation == 'SELECT':
            result = self.select_query(table_name)
        elif operation == 'INSERT':
            result = self.insert_query(table_name)
        elif operation == 'UPDATE':
            result = self.update_query(table_name)
        else:
            result = self.delete_query(table_name)
            
        duration = (time.time() - start_time) * 1000
        
        return {
            'operation': operation,
            'table': table_name,
            'duration': duration,
            'rows_affected': result,
            'timestamp': time.time()
        }
    
    def select_query(self, table_name):
        table = self.tables[table_name]
        if not table['rows']:
            return 0
            
        limit = random.randint(1, 100)
        offset = random.randint(0, max(0, len(table['rows']) - limit))
        
        time.sleep(random.uniform(0.001, 0.01))
        return min(limit, len(table['rows']) - offset)
    
    def insert_query(self, table_name):
        row = self.generate_row(table_name)
        with self.lock:
            self.tables[table_name]['rows'].append(row)
            self.tables[table_name]['row_count'] += 1
        time.sleep(random.uniform(0.002, 0.02))
        return 1
    
    def update_query(self, table_name):
        table = self.tables[table_name]
        if not table['rows']:
            return 0
            
        rows_to_update = random.randint(1, min(10, len(table['rows'])))
        time.sleep(random.uniform(0.003, 0.03))
        return rows_to_update
    
    def delete_query(self, table_name):
        table = self.tables[table_name]
        if not table['rows']:
            return 0
            
        rows_to_delete = random.randint(1, min(5, len(table['rows'])))
        with self.lock:
            table['rows'] = table['rows'][rows_to_delete:]
            table['row_count'] -= rows_to_delete
        return rows_to_delete
    
    def connection_pool(self, pool_size=5):
        for i in range(pool_size):
            self.connections.append({
                'id': i,
                'created': time.time(),
                'queries': 0,
                'active': random.choice([True, False])
            })
    
    def query_worker(self):
        while self.running:
            try:
                table_name = random.choice(list(self.tables.keys()))
                query = self.simulate_query(table_name)
                self.query_queue.put(query)
                
                for conn in self.connections:
                    if conn['active']:
                        conn['queries'] += 1
                        
            except Exception:
                pass
                
            time.sleep(random.uniform(0.01, 0.1))
    
    def start_workers(self, count=3):
        for i in range(count):
            t = threading.Thread(target=self.query_worker)
            t.daemon = True
            t.start()
    
    def get_stats(self):
        stats = {
            'tables': {},
            'total_rows': 0,
            'total_queries': self.query_queue.qsize(),
            'active_connections': len([c for c in self.connections if c['active']])
        }
        
        for table_name, table in self.tables.items():
            stats['tables'][table_name] = {
                'rows': table['row_count'],
                'columns': len(table['columns'])
            }
            stats['total_rows'] += table['row_count']
            
        return stats
    
    def run(self):
        for table_name in self.tables:
            self.populate_table(table_name, random.randint(100, 500))
            
        self.connection_pool(8)
        self.start_workers(4)
        
        for _ in range(100):
            self.simulate_query(random.choice(list(self.tables.keys())))
            
        stats = self.get_stats()
        self.running = False
        
        return stats

def main():
    db = DatabaseEmulator()
    stats = db.run()
    print(f"Database emulation: {stats['total_rows']} rows, {stats['total_queries']} queries")

if __name__ == "__main__":
    main()