"""Main analysis service that orchestrates the entire analysis process"""

from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.database import Project
from app.services.repo_parser import RepoParser
from app.services.ast_analyzer import ASTAnalyzer
from app.services.dependency_analyzer import DependencyAnalyzer
from app.services.graph_builder import GraphBuilder


class AnalysisService:
    """Orchestrate the complete repository analysis process"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo_parser = RepoParser()
        self.ast_analyzer = ASTAnalyzer()
        self.dependency_analyzer = DependencyAnalyzer()
    
    def analyze_repository(self, path: str, name: Optional[str] = None) -> Project:
        """
        Analyze a repository and store results in database
        
        Args:
            path: Local path or GitHub URL
            name: Optional project name
        
        Returns:
            Project object with analysis results
        """
        print(f"\n🔍 Starting analysis of: {path}")
        
        # Step 1: Get repository path (clone if needed)
        print("\n📥 Step 1: Preparing repository...")
        repo_path = self.repo_parser.get_repo_path(path)
        repo_root = Path(repo_path)
        
        # Step 2: Scan repository for files
        print("\n📂 Step 2: Scanning repository...")
        files_to_analyze, stats = self.repo_parser.scan_repository(repo_path)
        primary_language = self.repo_parser.get_primary_language(stats)
        
        print(f"   Found {stats['total_files']} files ({stats['total_lines']} lines)")
        print(f"   Languages: {stats['languages']}")
        print(f"   Primary language: {primary_language}")
        
        # Step 3: Create project in database
        print("\n💾 Step 3: Creating project record...")
        project_name = name or Path(path).name
        project = Project(
            name=project_name,
            repo_url=path if self.repo_parser.is_github_url(path) else None,
            local_path=repo_path,
            language=primary_language,
            total_files=stats['total_files'],
            total_lines=stats['total_lines'],
            status='analyzing'
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        
        print(f"   Created project: {project.name} (ID: {project.id})")
        
        try:
            # Step 4: Analyze each file
            print(f"\n🔬 Step 4: Analyzing {len(files_to_analyze)} files...")
            
            for i, file_path in enumerate(files_to_analyze, 1):
                try:
                    # Determine language
                    language = self.repo_parser.SUPPORTED_EXTENSIONS.get(file_path.suffix)
                    
                    if language:
                        # Analyze file
                        analysis = self.ast_analyzer.analyze_file(file_path, language)
                        
                        # Add to dependency analyzer
                        self.dependency_analyzer.add_file_analysis(file_path, analysis, repo_root)
                        
                        if i % 10 == 0 or i == len(files_to_analyze):
                            print(f"   Progress: {i}/{len(files_to_analyze)} files analyzed")
                
                except Exception as e:
                    print(f"   Warning: Failed to analyze {file_path}: {e}")
                    continue
            
            # Step 5: Extract dependencies
            print("\n🔗 Step 5: Extracting dependencies...")
            dependencies = self.dependency_analyzer.extract_dependencies()
            print(f"   Found {len(dependencies)} dependencies")
            
            # Step 6: Calculate importance scores
            print("\n📊 Step 6: Calculating importance scores...")
            importance_scores = self.dependency_analyzer.calculate_importance_scores()
            
            # Step 7: Build graph
            print("\n🕸️  Step 7: Building dependency graph...")
            graph_builder = GraphBuilder(project.id, repo_root)
            
            # Add file nodes
            for file_path, analysis in self.dependency_analyzer.file_map.items():
                language = self.repo_parser.SUPPORTED_EXTENSIONS.get(Path(file_path).suffix)
                graph_builder.add_file_node(file_path, language, analysis)
                
                # Add class nodes
                for class_info in analysis.get('classes', []):
                    graph_builder.add_class_node(file_path, class_info)
                
                # Add function nodes
                for func_info in analysis.get('functions', []):
                    graph_builder.add_function_node(file_path, func_info)
            
            # Add dependency edges
            for dep in dependencies:
                graph_builder.add_dependency_edge(
                    dep['source'],
                    dep['target'],
                    dep['type'],
                    dep['details']
                )
            
            # Update importance scores
            graph_builder.update_importance_scores(importance_scores)
            
            # Step 8: Save graph to database
            print("\n💾 Step 8: Saving graph to database...")
            graph_builder.save_to_database(self.db)
            
            # Step 9: Update project status
            print("\n✅ Step 9: Finalizing...")
            project.status = 'completed'
            project.last_analyzed = datetime.utcnow()
            self.db.commit()
            
            print(f"\n🎉 Analysis complete!")
            print(f"   Project: {project.name}")
            print(f"   Files: {project.total_files}")
            print(f"   Lines: {project.total_lines}")
            print(f"   Graph nodes: {len(graph_builder.nodes)}")
            print(f"   Graph edges: {len(graph_builder.edges)}")
            
            return project
        
        except Exception as e:
            # Rollback whatever partial write failed, then mark project as failed
            self.db.rollback()
            project.status = 'failed'
            self.db.commit()
            print(f"\n❌ Analysis failed: {e}")
            raise
        
        finally:
            # Cleanup temporary directory if created
            self.repo_parser.cleanup()
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """Get project by ID"""
        return self.db.query(Project).filter(Project.id == project_id).first()
    
    def list_projects(self) -> list[Project]:
        """List all projects"""
        return self.db.query(Project).order_by(Project.created_at.desc()).all()
    
    def delete_project(self, project_id: int) -> bool:
        """Delete a project and all its data"""
        project = self.get_project(project_id)
        if project:
            self.db.delete(project)
            self.db.commit()
            return True
        return False

# Made with Bob
