"""
Framework Engine for Personal AI Content Studio
Manages storytelling frameworks and content structure mapping

Phase 2: Foundational Services
Tasks: T016 (Framework Templates), T017 (Framework Mapping Logic)
"""

from backend.models.models import get_db_session, Framework
from typing import List, Dict, Optional
import json
import re


class FrameworkEngine:
    """Manages storytelling frameworks and content structure mapping"""
    
    def __init__(self):
        """Initialize framework engine and load frameworks from database"""
        self._frameworks_cache = None
        self._load_frameworks()
    
    def _load_frameworks(self):
        """Load all frameworks from database into cache"""
        session = get_db_session()
        try:
            frameworks = session.query(Framework).all()
            self._frameworks_cache = {}
            
            for fw in frameworks:
                self._frameworks_cache[fw.id] = {
                    'id': fw.id,
                    'name': fw.name,
                    'description': fw.description,
                    'steps': json.loads(fw.template_steps) if fw.template_steps else [],
                    'best_for': fw.best_for
                }
        finally:
            session.close()
    
    def get_frameworks(self) -> List[Dict]:
        """
        Get all available frameworks
        
        Returns:
            List of framework dicts with id, name, description, steps, best_for
        """
        if self._frameworks_cache is None:
            self._load_frameworks()
        
        return list(self._frameworks_cache.values())
    
    def get_framework(self, framework_id: str) -> Optional[Dict]:
        """
        Get framework by ID
        
        Args:
            framework_id: Framework identifier (e.g., 'ted-talk', 'listicle')
        
        Returns:
            Framework dict or None if not found
        """
        if self._frameworks_cache is None:
            self._load_frameworks()
        
        return self._frameworks_cache.get(framework_id)
    
    def recommend_framework(self, outline: Dict) -> str:
        """
        Recommend framework based on outline characteristics
        
        Args:
            outline: Dict with 'sections', 'content_angle', 'target_audience'
        
        Returns:
            framework_id (string)
            
        Logic:
            - If outline has numbered items → Listicle
            - If outline mentions "problem" or "solution" → Problem-Solution
            - If outline has "step" or "how to" → Tutorial
            - If outline compares options → Comparison
            - If outline has personal story or transformation → Hero's Journey
            - Default → TED Talk (versatile)
        """
        # Combine all text for analysis
        text_parts = []
        
        # Add sections (can be JSON string or list)
        sections = outline.get('sections', [])
        if isinstance(sections, str):
            try:
                sections = json.loads(sections)
            except json.JSONDecodeError:
                sections = [sections]
        
        # Extract section titles/text
        if isinstance(sections, list):
            for section in sections:
                if isinstance(section, dict):
                    text_parts.append(section.get('title', ''))
                    text_parts.append(section.get('content', ''))
                else:
                    text_parts.append(str(section))
        
        # Add other outline fields
        text_parts.append(outline.get('content_angle', ''))
        text_parts.append(outline.get('target_audience', ''))
        text_parts.append(outline.get('primary_intent', ''))
        
        # Combine and normalize text
        full_text = ' '.join(text_parts).lower()
        
        # Check for numbered/bulleted lists
        if re.search(r'\b\d+\s*(ways|tips|reasons|items|things|points)', full_text):
            return 'listicle'
        if re.search(r'(top|best)\s+\d+', full_text):
            return 'listicle'
        
        # Check for problem-solution pattern
        if 'problem' in full_text and 'solution' in full_text:
            return 'problem-solution'
        if re.search(r'\b(pain\s*point|challenge|issue|difficulty)', full_text) and \
           re.search(r'\b(solve|fix|remedy|address)', full_text):
            return 'problem-solution'
        
        # Check for tutorial/how-to
        if re.search(r'\b(step|how\s*to|guide|tutorial|walkthrough)', full_text):
            return 'tutorial'
        if re.search(r'\b(learn|build|create|make)\b', full_text) and \
           re.search(r'\b(step|instruction|process)', full_text):
            return 'tutorial'
        
        # Check for comparison
        if re.search(r'\b(vs|versus|compared\s*to|comparison)', full_text):
            return 'comparison'
        if re.search(r'\b(option|alternative|choice)\s+[a-c]\b', full_text, re.IGNORECASE):
            return 'comparison'
        if full_text.count(' or ') >= 2 and re.search(r'\b(which|choose|select|pick)', full_text):
            return 'comparison'
        
        # Check for hero's journey
        if re.search(r'\b(journey|transformation|story|narrative)', full_text):
            if re.search(r'\b(personal|my|experience|learned)', full_text):
                return 'heros-journey'
        if re.search(r'\b(overcome|challenge|obstacle|triumph|success\s*story)', full_text):
            return 'heros-journey'
        
        # Default to TED Talk (versatile)
        return 'ted-talk'
    
    def map_outline_to_framework(
        self,
        outline_sections: List[str],
        framework_id: str
    ) -> List[Dict]:
        """
        Map outline sections to framework steps
        
        Args:
            outline_sections: List of outline section titles
            framework_id: Framework to use
        
        Returns:
            List of mappings:
            [
                {
                    'framework_step': 'Hook',
                    'outline_section': 'Introduction',
                    'order': 1
                },
                ...
            ]
            
        Logic:
            Use keyword matching to align sections with framework steps.
        """
        framework = self.get_framework(framework_id)
        if not framework:
            raise ValueError(f"Framework '{framework_id}' not found")
        
        framework_steps = framework['steps']
        mappings = []
        
        # Create mapping based on framework type
        if framework_id == 'ted-talk':
            mappings = self._map_ted_talk(outline_sections, framework_steps)
        elif framework_id == 'heros-journey':
            mappings = self._map_heros_journey(outline_sections, framework_steps)
        elif framework_id == 'problem-solution':
            mappings = self._map_problem_solution(outline_sections, framework_steps)
        elif framework_id == 'listicle':
            mappings = self._map_listicle(outline_sections, framework_steps)
        elif framework_id == 'comparison':
            mappings = self._map_comparison(outline_sections, framework_steps)
        elif framework_id == 'tutorial':
            mappings = self._map_tutorial(outline_sections, framework_steps)
        else:
            # Generic mapping - sequential match
            mappings = self._map_generic(outline_sections, framework_steps)
        
        return mappings
    
    def _map_ted_talk(self, sections: List[str], steps: List[str]) -> List[Dict]:
        """Map sections to TED Talk framework steps"""
        mappings = []
        used_sections = set()
        
        # TED Talk steps: Hook, Build context, Key insight, Story examples, Call to action
        step_keywords = {
            'Hook': ['intro', 'hook', 'opening', 'start', 'begin'],
            'Build context': ['background', 'context', 'setting', 'why', 'history'],
            'Key insight': ['main', 'key', 'insight', 'point', 'core', 'central', 'idea'],
            'Story examples': ['example', 'story', 'case', 'illustration', 'anecdote'],
            'Call to action': ['conclusion', 'action', 'next', 'takeaway', 'summary', 'end']
        }
        
        for step in steps:
            best_match = None
            best_score = 0
            
            keywords = step_keywords.get(step, [])
            
            for i, section in enumerate(sections):
                if i in used_sections:
                    continue
                
                section_lower = section.lower()
                score = sum(1 for kw in keywords if kw in section_lower)
                
                # First section often maps to Hook
                if step == 'Hook' and i == 0:
                    score += 2
                
                # Last section often maps to Call to action
                if step == 'Call to action' and i == len(sections) - 1:
                    score += 2
                
                if score > best_score:
                    best_score = score
                    best_match = i
            
            if best_match is not None:
                mappings.append({
                    'framework_step': step,
                    'outline_section': sections[best_match],
                    'order': len(mappings) + 1
                })
                used_sections.add(best_match)
        
        return mappings
    
    def _map_heros_journey(self, sections: List[str], steps: List[str]) -> List[Dict]:
        """Map sections to Hero's Journey framework steps"""
        mappings = []
        used_sections = set()
        
        step_keywords = {
            'Call to action': ['intro', 'start', 'beginning', 'call'],
            'Refusal': ['hesitation', 'doubt', 'refuse', 'reluctan'],
            'Meeting mentor': ['mentor', 'guide', 'help', 'advice', 'support'],
            'Crossing threshold': ['decision', 'commit', 'start', 'journey', 'begin'],
            'Tests': ['challenge', 'test', 'obstacle', 'difficulty', 'trial'],
            'Ordeal': ['crisis', 'ordeal', 'struggle', 'problem', 'worst'],
            'Reward': ['success', 'reward', 'achievement', 'victory', 'breakthrough'],
            'Return': ['return', 'conclusion', 'lesson', 'takeaway', 'end']
        }
        
        for step in steps:
            best_match = None
            best_score = 0
            keywords = step_keywords.get(step, [])
            
            for i, section in enumerate(sections):
                if i in used_sections:
                    continue
                
                section_lower = section.lower()
                score = sum(1 for kw in keywords if kw in section_lower)
                
                if score > best_score:
                    best_score = score
                    best_match = i
            
            if best_match is not None:
                mappings.append({
                    'framework_step': step,
                    'outline_section': sections[best_match],
                    'order': len(mappings) + 1
                })
                used_sections.add(best_match)
        
        return mappings
    
    def _map_problem_solution(self, sections: List[str], steps: List[str]) -> List[Dict]:
        """Map sections to Problem-Solution framework steps"""
        mappings = []
        used_sections = set()
        
        step_keywords = {
            'The problem': ['problem', 'issue', 'challenge', 'pain', 'difficulty'],
            'Why it matters': ['why', 'important', 'matter', 'impact', 'consequence'],
            'Current approaches': ['current', 'existing', 'traditional', 'approach', 'attempt'],
            'Our solution': ['solution', 'proposal', 'our', 'approach', 'method'],
            'Benefits': ['benefit', 'advantage', 'value', 'gain', 'positive'],
            'Implementation': ['implementation', 'how', 'step', 'action', 'deploy']
        }
        
        for step in steps:
            best_match = None
            best_score = 0
            keywords = step_keywords.get(step, [])
            
            for i, section in enumerate(sections):
                if i in used_sections:
                    continue
                
                section_lower = section.lower()
                score = sum(1 for kw in keywords if kw in section_lower)
                
                if score > best_score:
                    best_score = score
                    best_match = i
            
            if best_match is not None:
                mappings.append({
                    'framework_step': step,
                    'outline_section': sections[best_match],
                    'order': len(mappings) + 1
                })
                used_sections.add(best_match)
        
        return mappings
    
    def _map_listicle(self, sections: List[str], steps: List[str]) -> List[Dict]:
        """Map sections to Listicle framework steps"""
        mappings = []
        
        # Listicle: Intro, Item 1, Item 2, Item 3+, Conclusion
        if len(sections) == 0:
            return mappings
        
        # First section → Intro
        mappings.append({
            'framework_step': 'Intro',
            'outline_section': sections[0],
            'order': 1
        })
        
        # Middle sections → Items
        middle_sections = sections[1:-1] if len(sections) > 2 else sections[1:]
        
        for i, section in enumerate(middle_sections):
            if i == 0:
                step = 'Item 1'
            elif i == 1:
                step = 'Item 2'
            else:
                step = 'Item 3+'
            
            mappings.append({
                'framework_step': step,
                'outline_section': section,
                'order': len(mappings) + 1
            })
        
        # Last section → Conclusion (if more than 1 section)
        if len(sections) > 1:
            mappings.append({
                'framework_step': 'Conclusion',
                'outline_section': sections[-1],
                'order': len(mappings) + 1
            })
        
        return mappings
    
    def _map_comparison(self, sections: List[str], steps: List[str]) -> List[Dict]:
        """Map sections to Comparison framework steps"""
        mappings = []
        used_sections = set()
        
        step_keywords = {
            'Intro': ['intro', 'overview', 'comparison', 'start'],
            'Criteria': ['criteria', 'factor', 'consider', 'metric', 'feature'],
            'Option A': ['option', 'first', 'alternative', 'choice'],
            'Option B': ['option', 'second', 'alternative', 'choice'],
            'Option C': ['option', 'third', 'alternative', 'choice'],
            'Recommendation': ['recommend', 'conclusion', 'verdict', 'best', 'choose']
        }
        
        for step in steps:
            best_match = None
            best_score = 0
            keywords = step_keywords.get(step, [])
            
            for i, section in enumerate(sections):
                if i in used_sections:
                    continue
                
                section_lower = section.lower()
                score = sum(1 for kw in keywords if kw in section_lower)
                
                # First section often maps to Intro
                if step == 'Intro' and i == 0:
                    score += 2
                
                # Last section often maps to Recommendation
                if step == 'Recommendation' and i == len(sections) - 1:
                    score += 2
                
                if score > best_score:
                    best_score = score
                    best_match = i
            
            if best_match is not None:
                mappings.append({
                    'framework_step': step,
                    'outline_section': sections[best_match],
                    'order': len(mappings) + 1
                })
                used_sections.add(best_match)
        
        return mappings
    
    def _map_tutorial(self, sections: List[str], steps: List[str]) -> List[Dict]:
        """Map sections to Tutorial framework steps"""
        mappings = []
        used_sections = set()
        
        step_keywords = {
            'Intro & tools needed': ['intro', 'tool', 'requirement', 'need', 'prerequisite'],
            'Step 1': ['step', 'first', 'start', 'begin', '1'],
            'Step 2': ['step', 'second', 'next', '2'],
            'Step 3+': ['step', 'third', 'additional', '3', '4', '5'],
            'Expected result': ['result', 'outcome', 'expect', 'output', 'final'],
            'Troubleshooting': ['troubleshoot', 'issue', 'problem', 'error', 'debug']
        }
        
        for step in steps:
            best_match = None
            best_score = 0
            keywords = step_keywords.get(step, [])
            
            for i, section in enumerate(sections):
                if i in used_sections:
                    continue
                
                section_lower = section.lower()
                score = sum(1 for kw in keywords if kw in section_lower)
                
                # First section often maps to Intro
                if step == 'Intro & tools needed' and i == 0:
                    score += 2
                
                # Last section may map to Troubleshooting or Expected result
                if i == len(sections) - 1:
                    if step == 'Troubleshooting':
                        score += 1
                    elif step == 'Expected result':
                        score += 1
                
                if score > best_score:
                    best_score = score
                    best_match = i
            
            if best_match is not None:
                mappings.append({
                    'framework_step': step,
                    'outline_section': sections[best_match],
                    'order': len(mappings) + 1
                })
                used_sections.add(best_match)
        
        return mappings
    
    def _map_generic(self, sections: List[str], steps: List[str]) -> List[Dict]:
        """Generic sequential mapping when specific framework logic not available"""
        mappings = []
        
        for i, section in enumerate(sections):
            # Map to framework steps sequentially, cycling if more sections than steps
            step_index = i % len(steps) if steps else 0
            
            if steps:
                mappings.append({
                    'framework_step': steps[step_index],
                    'outline_section': section,
                    'order': i + 1
                })
        
        return mappings
    
    def validate_mapping(
        self,
        mapping: List[Dict],
        framework_id: str
    ) -> Dict:
        """
        Validate that mapping covers all framework steps
        
        Args:
            mapping: List of step mappings
            framework_id: Framework to validate against
        
        Returns:
            {
                'is_complete': bool,
                'missing_steps': List[str],
                'unmapped_sections': List[str]
            }
        """
        framework = self.get_framework(framework_id)
        if not framework:
            raise ValueError(f"Framework '{framework_id}' not found")
        
        framework_steps = set(framework['steps'])
        mapped_steps = set(m['framework_step'] for m in mapping)
        
        missing_steps = list(framework_steps - mapped_steps)
        
        # Note: We can't determine unmapped sections without the original section list
        # This would need to be passed as a parameter if needed
        
        return {
            'is_complete': len(missing_steps) == 0,
            'missing_steps': missing_steps,
            'unmapped_sections': []  # Cannot determine without original section list
        }


# Singleton instance cache
_engine_instance = None


def get_framework_engine() -> FrameworkEngine:
    """
    Get singleton instance of FrameworkEngine
    
    Returns:
        FrameworkEngine instance
    """
    global _engine_instance
    
    if _engine_instance is None:
        _engine_instance = FrameworkEngine()
    
    return _engine_instance
