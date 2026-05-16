"""AI-powered documentation generator using watsonx.ai"""

import re
from typing import Dict, Any, List
from pathlib import Path
import json

from app.services.watsonx_client import watsonx_client
from app.database import Project


# Patterns to strip from LLM output - conversational filler common in llama models
_FILLER_PATTERNS = [
    r'^(please\s+let\s+me\s+know|let\s+me\s+know\s+if|i\s+am\s+here\s+to\s+help|i\s+hope\s+this|best\s+regards|note:\s+i\s+have\s+follow|i\s+can\s+also|i\s+have\s+completed|please\s+provide\s+more|also,\s+please|also\s+let\s+me|for\s+questions,\s+comments|this\s+document\s+is\s+licensed|revision\s+history|acknowledgments|disclaimer|end\s+of\s+document|\[your\s+name\]|\[insert\s+contact|\[End\])',
    r'^note:\s+the\s+(end\s+of\s+document|revision\s+history|references\s+provided|contact\s+information|license\s+information|index\s+is\s+for|appendices\s+are)',
]
_FILLER_RE = re.compile('|'.join(_FILLER_PATTERNS), re.IGNORECASE)

# Stop at these section titles — they signal the model went beyond the ask
_STOP_HEADERS = re.compile(
    r'^#{1,3}\s*(revision\s+history|acknowledgments|disclaimer|license|contact|appendix|index|end\s+of\s+document)',
    re.IGNORECASE | re.MULTILINE,
)


def _clean_output(text: str) -> str:
    """Strip conversational filler and runaway sections from LLM output."""
    # Cut at stop headers
    m = _STOP_HEADERS.search(text)
    if m:
        text = text[:m.start()].rstrip()

    lines = text.splitlines()
    cleaned: list[str] = []
    blank_run = 0

    for line in lines:
        stripped = line.strip()

        # Drop filler lines
        if stripped and _FILLER_RE.match(stripped):
            continue

        # Collapse runs of blank lines to at most one
        if not stripped:
            blank_run += 1
            if blank_run <= 1:
                cleaned.append('')
        else:
            blank_run = 0
            cleaned.append(line)

    return '\n'.join(cleaned).strip()


_SYSTEM_PROMPT = (
    "You are a senior software engineer writing technical documentation. "
    "Output ONLY the markdown documentation requested — no greetings, no sign-offs, "
    "no 'Note:', no 'Let me know', no 'I hope this helps', no Revision History, "
    "no Acknowledgments, no Disclaimer sections. "
    "Use markdown headings and bullet points. Stop as soon as the documentation is complete."
)

_PROMPT_FOOTER = (
    "\n\nWrite ONLY the sections listed above. No extra sections, no conversational text."
)


class PromptTemplates:
    """Prompt templates for documentation generation"""

    @staticmethod
    def project_overview(project_data: Dict[str, Any]) -> str:
        return f"""Generate a concise project overview documentation in markdown format.

Project Name: {project_data.get('name', 'Unknown')}
Primary Language: {project_data.get('primary_language', 'Unknown')}
Total Files: {project_data.get('total_files', 0)}
Total Lines: {project_data.get('total_lines', 0)}

File Structure:
{json.dumps(project_data.get('file_structure', {}), indent=2)}

Key Modules:
{json.dumps(project_data.get('modules', []), indent=2)}

Write the following sections and NOTHING else:
## Project Purpose
## Key Features
## Technology Stack
## Project Structure
{_PROMPT_FOOTER}"""

    @staticmethod
    def module_explanation(module_data: Dict[str, Any]) -> str:
        return f"""Generate concise module documentation in markdown format.

Module: {module_data.get('name', 'Unknown')}
File Path: {module_data.get('path', 'Unknown')}
Language: {module_data.get('language', 'Unknown')}
Lines of Code: {module_data.get('lines', 0)}

Functions/Classes:
{json.dumps(module_data.get('definitions', []), indent=2)}

Dependencies:
{json.dumps(module_data.get('dependencies', []), indent=2)}

Write the following sections and NOTHING else:
## Purpose
## Key Components
## Dependencies
## Usage
{_PROMPT_FOOTER}"""

    @staticmethod
    def getting_started(project_data: Dict[str, Any]) -> str:
        return f"""Generate a getting started guide in markdown format for developers new to this project.

Project Name: {project_data.get('name', 'Unknown')}
Primary Language: {project_data.get('primary_language', 'Unknown')}
Technologies: {json.dumps(project_data.get('technologies', []), indent=2)}

Project Structure:
{json.dumps(project_data.get('structure_summary', {}), indent=2)}

Write the following sections and NOTHING else:
## Prerequisites
## Installation
## Configuration
## Running the Project
## Common Tasks
{_PROMPT_FOOTER}"""

    @staticmethod
    def api_documentation(api_data: Dict[str, Any]) -> str:
        return f"""Generate API documentation in markdown format.

API Endpoints:
{json.dumps(api_data.get('endpoints', []), indent=2)}

Write the following sections and NOTHING else:
## API Overview
## Authentication
## Endpoints
## Error Handling
{_PROMPT_FOOTER}"""

    @staticmethod
    def architecture_diagram(project_data: Dict[str, Any]) -> str:
        return f"""Generate a software architecture description in markdown format.

Project: {project_data.get('name', 'Unknown')}
Components: {json.dumps(project_data.get('components', []), indent=2)}
Dependencies: {json.dumps(project_data.get('dependency_graph', {}), indent=2)}

Write the following sections and NOTHING else:
## Architecture Overview
## Components
## Data Flow
## Design Patterns
{_PROMPT_FOOTER}"""


class DocGenerator:
    """Generate AI-powered documentation for code projects"""

    def __init__(self):
        self.client = watsonx_client
        self.templates = PromptTemplates()

    def _chat(self, user_prompt: str, max_tokens: int = 1024) -> str:
        """Send a documentation prompt to llama-3-3-70b via the chat API."""
        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        raw = self.client.chat(messages=messages, max_tokens=max_tokens, temperature=0.2)
        return _clean_output(raw)

    def generate_project_overview(self, project: Project) -> str:
        project_data = {
            'name': project.name,
            'primary_language': project.language or 'Unknown',
            'total_files': project.total_files or 0,
            'total_lines': project.total_lines or 0,
            'file_structure': self._get_file_structure(project),
            'modules': self._get_key_modules(project),
        }
        prompt = self.templates.project_overview(project_data)
        return self._chat(prompt, max_tokens=1024)

    def generate_module_docs(self, project: Project, module_path: str) -> str:
        module_data = self._extract_module_data(project, module_path)
        prompt = self.templates.module_explanation(module_data)
        return self._chat(prompt, max_tokens=800)

    def generate_getting_started(self, project: Project) -> str:
        project_data = {
            'name': project.name,
            'primary_language': project.language or 'Unknown',
            'technologies': self._detect_technologies(project),
            'structure_summary': self._get_structure_summary(project),
        }
        prompt = self.templates.getting_started(project_data)
        return self._chat(prompt, max_tokens=1024)

    def generate_api_docs(self, project: Project) -> str:
        api_data = {'endpoints': self._extract_api_endpoints(project)}
        prompt = self.templates.api_documentation(api_data)
        return self._chat(prompt, max_tokens=1024)

    def generate_architecture_docs(self, project: Project) -> str:
        mermaid = self._generate_mermaid_diagram(project)
        project_data = {
            'name': project.name,
            'components': self._identify_components(project),
            'dependency_graph': self._get_dependency_summary(project),
        }
        prompt = self.templates.architecture_diagram(project_data)
        text = self._chat(prompt, max_tokens=800)
        if mermaid:
            return f"```mermaid\n{mermaid}\n```\n\n{text}"
        return text

    def _generate_mermaid_diagram(self, project: Project) -> str:
        """Build a Mermaid flowchart directly from graph nodes and edges — no LLM needed."""
        # Map node_id → file_path
        node_to_file: Dict[str, str] = {}
        file_nodes: Dict[str, Any] = {}
        for node in project.graph_nodes:
            if node.file_path:
                node_to_file[node.node_id] = node.file_path
                if node.node_type == 'file':
                    file_nodes[node.file_path] = node

        if not file_nodes:
            return ''

        # Derive file-to-file edges
        file_edges: set = set()
        for edge in project.graph_edges:
            src = node_to_file.get(edge.source_node_id)
            tgt = node_to_file.get(edge.target_node_id)
            if src and tgt and src != tgt:
                file_edges.add((src, tgt))

        # Keep top 20 files by importance so the diagram stays readable
        top_files = {
            fp for fp, _ in sorted(
                file_nodes.items(),
                key=lambda x: x[1].importance_score or 0,
                reverse=True
            )[:20]
        }

        # Only keep edges between top files
        top_edges = [(s, t) for s, t in file_edges if s in top_files and t in top_files]

        # Sanitise path → valid Mermaid node ID
        def mid(p: str) -> str:
            return p.replace('/', '__').replace('.', '_').replace('-', '_').replace(' ', '_')

        def mlabel(p: str) -> str:
            return Path(p).name

        # Group by top-level directory for subgraphs
        groups: Dict[str, List[str]] = {}
        for fp in top_files:
            parts = Path(fp).parts
            grp = parts[0] if len(parts) > 1 else '__root__'
            groups.setdefault(grp, []).append(fp)

        lines = ['flowchart TD']

        for grp, files in sorted(groups.items()):
            if grp == '__root__':
                for fp in sorted(files):
                    lines.append(f'    {mid(fp)}["{mlabel(fp)}"]')
            else:
                safe_grp = mid(grp)
                lines.append(f'    subgraph {safe_grp}["{grp}"]')
                for fp in sorted(files):
                    lines.append(f'        {mid(fp)}["{mlabel(fp)}"]')
                lines.append('    end')

        for src, tgt in top_edges:
            lines.append(f'    {mid(src)} --> {mid(tgt)}')

        # Dark-theme node styling
        lines.append('    classDef default fill:#1e293b,stroke:#475569,color:#94a3b8,rx:6')
        lines.append('    classDef highlight fill:#1e3a5f,stroke:#3b82f6,color:#93c5fd,rx:6')

        return '\n'.join(lines)

    def generate_all_docs(self, project: Project) -> Dict[str, str]:
        print("📝 Generating project overview...")
        overview = self.generate_project_overview(project)

        print("📝 Generating getting started guide...")
        getting_started = self.generate_getting_started(project)

        print("📝 Generating architecture documentation...")
        architecture = self.generate_architecture_docs(project)

        api_docs = ""
        if self._has_api_endpoints(project):
            print("📝 Generating API documentation...")
            api_docs = self.generate_api_docs(project)

        return {
            'overview': overview,
            'getting_started': getting_started,
            'architecture': architecture,
            'api': api_docs,
        }

    # ── Helper methods ──────────────────────────────────────────────────────

    def _get_file_structure(self, project: Project) -> Dict[str, Any]:
        file_structure: Dict[str, Any] = {}
        for node in project.graph_nodes:
            if node.file_path:
                if node.file_path not in file_structure:
                    file_structure[node.file_path] = {'type': node.node_type, 'nodes': []}
                file_structure[node.file_path]['nodes'].append(
                    {'name': node.name, 'type': node.node_type, 'line': node.line_number}
                )
        return file_structure

    def _get_key_modules(self, project: Project) -> List[Dict[str, Any]]:
        modules: Dict[str, Any] = {}
        for node in project.graph_nodes:
            if node.file_path:
                if node.file_path not in modules:
                    modules[node.file_path] = {
                        'name': node.file_path.split('/')[-1],
                        'path': node.file_path,
                        'type': node.node_type,
                        'definitions': [],
                        'importance': node.importance_score or 0,
                    }
                modules[node.file_path]['definitions'].append(
                    {'name': node.name, 'type': node.node_type, 'line': node.line_number}
                )
        module_list = list(modules.values())
        return sorted(module_list, key=lambda x: x.get('importance', 0), reverse=True)[:10]

    def _extract_module_data(self, project: Project, module_path: str) -> Dict[str, Any]:
        module_data: Dict[str, Any] = {
            'name': module_path.split('/')[-1],
            'path': module_path,
            'definitions': [],
            'dependencies': [],
        }
        for node in project.graph_nodes:
            if node.file_path == module_path:
                module_data['definitions'].append(
                    {'name': node.name, 'type': node.node_type, 'line': node.line_number}
                )
        for edge in project.graph_edges:
            source_node = next((n for n in project.graph_nodes if n.node_id == edge.source_node_id), None)
            target_node = next((n for n in project.graph_nodes if n.node_id == edge.target_node_id), None)
            if source_node and source_node.file_path == module_path and target_node:
                module_data['dependencies'].append({'target': target_node.name, 'type': edge.edge_type})
        return module_data

    def _detect_technologies(self, project: Project) -> List[str]:
        technologies = []
        if project.language:
            technologies.append(project.language)
        file_paths_str = ' '.join(
            node.file_path for node in project.graph_nodes if node.file_path
        )
        checks = [
            ('package.json', 'Node.js'),
            ('requirements.txt', 'Python'),
            ('pom.xml', 'Maven'),
            ('build.gradle', 'Gradle'),
            ('.tsx', 'React'),
            ('.jsx', 'React'),
            ('Dockerfile', 'Docker'),
        ]
        seen = set(technologies)
        for pattern, tech in checks:
            if pattern in file_paths_str and tech not in seen:
                technologies.append(tech)
                seen.add(tech)
        return technologies or [project.language or 'Unknown']

    def _get_structure_summary(self, project: Project) -> Dict[str, Any]:
        node_types: Dict[str, int] = {}
        for node in project.graph_nodes:
            node_types[node.node_type] = node_types.get(node.node_type, 0) + 1
        return {
            'total_files': project.total_files or 0,
            'total_lines': project.total_lines or 0,
            'total_nodes': len(project.graph_nodes),
            'node_types': node_types,
        }

    def _extract_api_endpoints(self, project: Project) -> List[Dict[str, Any]]:
        return []

    def _has_api_endpoints(self, project: Project) -> bool:
        return len(self._extract_api_endpoints(project)) > 0

    def _identify_components(self, project: Project) -> List[Dict[str, Any]]:
        components: Dict[str, Any] = {}
        for node in project.graph_nodes:
            if node.file_path:
                parts = Path(node.file_path).parts
                if len(parts) > 1:
                    component = parts[0]
                    if component not in components:
                        components[component] = {'name': component, 'files': set(), 'node_count': 0}
                    components[component]['files'].add(node.file_path)
                    components[component]['node_count'] += 1
        return [
            {'name': name, 'file_count': len(data['files']), 'node_count': data['node_count']}
            for name, data in components.items()
        ]

    def _get_dependency_summary(self, project: Project) -> Dict[str, Any]:
        edge_types: Dict[str, int] = {}
        for edge in project.graph_edges:
            edge_types[edge.edge_type] = edge_types.get(edge.edge_type, 0) + 1
        return {
            'total_edges': len(project.graph_edges),
            'edge_types': edge_types,
            'total_nodes': len(project.graph_nodes),
        }


# Global instance
doc_generator = DocGenerator()

# Made with Bob
