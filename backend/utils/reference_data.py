"""
Reference Data Manager
Loads and provides access to framework, platform, focus area, and visual type data
"""

from typing import List, Dict, Optional
import json
from backend.models.models import get_db_session, Framework, Platform, FocusArea, VisualType


class ReferenceDataManager:
    """Manages read access to reference data"""
    
    def __init__(self):
        self.session = get_db_session()
        self._frameworks_cache = None
        self._platforms_cache = None
        self._focus_areas_cache = None
        self._visual_types_cache = None
    
    # ============= Frameworks =============
    
    def get_frameworks(self) -> List[Dict]:
        """Get all available frameworks"""
        if self._frameworks_cache is None:
            frameworks = self.session.query(Framework).all()
            self._frameworks_cache = [
                {
                    'id': f.id,
                    'name': f.name,
                    'description': f.description,
                    'template_steps': json.loads(f.template_steps) if f.template_steps else [],
                    'best_for': f.best_for,
                } for f in frameworks
            ]
        return self._frameworks_cache
    
    def get_framework(self, framework_id: str) -> Optional[Dict]:
        """Get framework by ID"""
        frameworks = self.get_frameworks()
        return next((f for f in frameworks if f['id'] == framework_id), None)
    
    def get_framework_by_name(self, name: str) -> Optional[Dict]:
        """Get framework by name"""
        frameworks = self.get_frameworks()
        return next((f for f in frameworks if f['name'].lower() == name.lower()), None)
    
    # ============= Platforms =============
    
    def get_platforms(self) -> List[Dict]:
        """Get all available platforms"""
        if self._platforms_cache is None:
            platforms = self.session.query(Platform).all()
            self._platforms_cache = [
                {
                    'id': p.id,
                    'name': p.name,
                    'description': p.description,
                    'tone': p.tone,
                    'format': p.format,
                    'min_length': p.min_length,
                    'max_length': p.max_length,
                    'visual_requirements': p.visual_requirements,
                } for p in platforms
            ]
        return self._platforms_cache
    
    def get_platform(self, platform_id: str) -> Optional[Dict]:
        """Get platform by ID"""
        platforms = self.get_platforms()
        return next((p for p in platforms if p['id'] == platform_id), None)
    
    def get_platform_by_name(self, name: str) -> Optional[Dict]:
        """Get platform by name"""
        platforms = self.get_platforms()
        return next((p for p in platforms if p['name'].lower() == name.lower()), None)
    
    def get_all_platform_ids(self) -> List[str]:
        """Get list of all platform IDs"""
        return [p['id'] for p in self.get_platforms()]
    
    def get_all_platform_names(self) -> List[str]:
        """Get list of all platform names"""
        return [p['name'] for p in self.get_platforms()]
    
    # ============= Focus Areas =============
    
    def get_focus_areas(self, active_only: bool = True) -> List[Dict]:
        """Get focus areas for topic classification"""
        if self._focus_areas_cache is None:
            query = self.session.query(FocusArea)
            if active_only:
                query = query.filter(FocusArea.is_active == 1)
            
            areas = query.all()
            self._focus_areas_cache = [
                {
                    'id': a.id,
                    'name': a.name,
                    'description': a.description,
                    'is_active': bool(a.is_active),
                } for a in areas
            ]
        return self._focus_areas_cache
    
    def get_focus_area(self, area_id: str) -> Optional[Dict]:
        """Get focus area by ID"""
        areas = self.get_focus_areas(active_only=False)
        return next((a for a in areas if a['id'] == area_id), None)
    
    def get_focus_area_by_name(self, name: str) -> Optional[Dict]:
        """Get focus area by name"""
        areas = self.get_focus_areas(active_only=False)
        return next((a for a in areas if a['name'].lower() == name.lower()), None)
    
    def get_active_focus_areas(self) -> List[str]:
        """Get list of active focus area names"""
        areas = self.get_focus_areas(active_only=True)
        return [a['name'] for a in areas]
    
    # ============= Visual Types =============
    
    def get_visual_types(self) -> List[Dict]:
        """Get all visual types"""
        if self._visual_types_cache is None:
            types = self.session.query(VisualType).all()
            self._visual_types_cache = [
                {
                    'id': v.id,
                    'name': v.name,
                    'description': v.description,
                    'mermaid_capable': bool(v.mermaid_capable),
                } for v in types
            ]
        return self._visual_types_cache
    
    def get_visual_type(self, type_id: str) -> Optional[Dict]:
        """Get visual type by ID"""
        types = self.get_visual_types()
        return next((t for t in types if t['id'] == type_id), None)
    
    def get_mermaid_visual_types(self) -> List[Dict]:
        """Get visual types that support Mermaid diagrams"""
        types = self.get_visual_types()
        return [t for t in types if t['mermaid_capable']]
    
    # ============= Cache Management =============
    
    def clear_cache(self):
        """Clear all caches (useful after data updates)"""
        self._frameworks_cache = None
        self._platforms_cache = None
        self._focus_areas_cache = None
        self._visual_types_cache = None
    
    def refresh(self):
        """Refresh all cached data from database"""
        self.clear_cache()
        # Trigger reload
        self.get_frameworks()
        self.get_platforms()
        self.get_focus_areas()
        self.get_visual_types()


# Global instance
_reference_data = None


def get_reference_data() -> ReferenceDataManager:
    """Get global reference data manager instance"""
    global _reference_data
    if _reference_data is None:
        _reference_data = ReferenceDataManager()
    return _reference_data


# Convenience functions for templates/views
def get_frameworks_for_template() -> List[Dict]:
    """Get frameworks for frontend selection"""
    return get_reference_data().get_frameworks()


def get_platforms_for_template() -> List[Dict]:
    """Get platforms for frontend display"""
    return get_reference_data().get_platforms()


def get_focus_areas_for_validation() -> List[str]:
    """Get active focus areas for input validation"""
    return get_reference_data().get_active_focus_areas()
