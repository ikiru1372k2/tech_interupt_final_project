#!/usr/bin/env python3
"""
Local model storage and management system
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ModelStorage:
    """Local database storage for ML models and metadata."""
    
    def __init__(self, db_path: str = "models.db"):
        """Initialize the model storage database."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database for model storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create models table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT UNIQUE NOT NULL,
                model_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metrics TEXT,
                feature_count INTEGER,
                training_samples INTEGER,
                effort_limit REAL,
                is_active BOOLEAN DEFAULT 0
            )
        ''')
        
        # Create model versions table for tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER,
                version TEXT NOT NULL,
                file_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metrics TEXT,
                FOREIGN KEY (model_id) REFERENCES models (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Model storage database initialized")
    
    def save_model(self, model_name: str, model_type: str, file_path: str, 
                   metrics: Dict[str, Any], feature_count: int, 
                   training_samples: int, effort_limit: float) -> int:
        """Save model metadata to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Deactivate all existing models
        cursor.execute('UPDATE models SET is_active = 0')
        
        # Insert new model
        cursor.execute('''
            INSERT OR REPLACE INTO models 
            (model_name, model_type, file_path, metrics, feature_count, 
             training_samples, effort_limit, is_active, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
        ''', (
            model_name, model_type, file_path, json.dumps(metrics),
            feature_count, training_samples, effort_limit
        ))
        
        model_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Model saved to database: {model_name}")
        return model_id
    
    def get_active_model(self) -> Optional[Dict[str, Any]]:
        """Get the currently active model."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM models WHERE is_active = 1 ORDER BY updated_at DESC LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'model_name': row[1],
                'model_type': row[2],
                'file_path': row[3],
                'created_at': row[4],
                'updated_at': row[5],
                'metrics': json.loads(row[6]) if row[6] else {},
                'feature_count': row[7],
                'training_samples': row[8],
                'effort_limit': row[9],
                'is_active': bool(row[10])
            }
        return None
    
    def get_all_models(self) -> List[Dict[str, Any]]:
        """Get all saved models."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM models ORDER BY updated_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        models = []
        for row in rows:
            models.append({
                'id': row[0],
                'model_name': row[1],
                'model_type': row[2],
                'file_path': row[3],
                'created_at': row[4],
                'updated_at': row[5],
                'metrics': json.loads(row[6]) if row[6] else {},
                'feature_count': row[7],
                'training_samples': row[8],
                'effort_limit': row[9],
                'is_active': bool(row[10])
            })
        
        return models
    
    def delete_model(self, model_id: int) -> bool:
        """Delete a model from database and file system."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get model info
        cursor.execute('SELECT file_path FROM models WHERE id = ?', (model_id,))
        row = cursor.fetchone()
        
        if row:
            file_path = row[0]
            
            # Delete from database
            cursor.execute('DELETE FROM models WHERE id = ?', (model_id,))
            conn.commit()
            conn.close()
            
            # Delete file if exists
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Model file deleted: {file_path}")
            
            logger.info(f"Model deleted from database: ID {model_id}")
            return True
        
        conn.close()
        return False
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get model storage statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count total models
        cursor.execute('SELECT COUNT(*) FROM models')
        total_models = cursor.fetchone()[0]
        
        # Count active models
        cursor.execute('SELECT COUNT(*) FROM models WHERE is_active = 1')
        active_models = cursor.fetchone()[0]
        
        # Get latest model info
        cursor.execute('''
            SELECT model_type, updated_at FROM models 
            ORDER BY updated_at DESC LIMIT 1
        ''')
        latest = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_models': total_models,
            'active_models': active_models,
            'latest_model_type': latest[0] if latest else None,
            'latest_update': latest[1] if latest else None
        }



