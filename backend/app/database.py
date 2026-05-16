"""Database setup and initialization for CodeLens"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Float, TIMESTAMP, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from app.config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


# Database Models
class Project(Base):
    """Project model"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    repo_url = Column(String)
    local_path = Column(String, nullable=False)
    language = Column(String)
    total_files = Column(Integer)
    total_lines = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    last_analyzed = Column(TIMESTAMP)
    status = Column(String, default="pending")
    
    # Relationships
    graph_nodes = relationship("GraphNode", back_populates="project", cascade="all, delete-orphan")
    graph_edges = relationship("GraphEdge", back_populates="project", cascade="all, delete-orphan")
    documentation = relationship("Documentation", back_populates="project", cascade="all, delete-orphan")
    qa_history = relationship("QAHistory", back_populates="project", cascade="all, delete-orphan")
    code_embeddings = relationship("CodeEmbedding", back_populates="project", cascade="all, delete-orphan")
    tech_debt = relationship("TechDebt", back_populates="project", cascade="all, delete-orphan")


class GraphNode(Base):
    """Graph node model"""
    __tablename__ = "graph_nodes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    node_id = Column(String, unique=True, nullable=False)
    node_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    file_path = Column(String)
    line_number = Column(Integer)
    importance_score = Column(Float)
    node_metadata = Column(Text)  # JSON stored as text
    
    # Relationships
    project = relationship("Project", back_populates="graph_nodes")
    
    __table_args__ = (
        Index("idx_graph_nodes_project", "project_id"),
    )


class GraphEdge(Base):
    """Graph edge model"""
    __tablename__ = "graph_edges"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    source_node_id = Column(String, nullable=False)
    target_node_id = Column(String, nullable=False)
    edge_type = Column(String, nullable=False)
    weight = Column(Integer, default=1)
    
    # Relationships
    project = relationship("Project", back_populates="graph_edges")
    
    __table_args__ = (
        Index("idx_graph_edges_project", "project_id"),
        Index("idx_graph_edges_source", "source_node_id"),
        Index("idx_graph_edges_target", "target_node_id"),
    )


class Documentation(Base):
    """Documentation model"""
    __tablename__ = "documentation"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    section_name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    order_index = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="documentation")
    
    __table_args__ = (
        Index("idx_documentation_project", "project_id"),
    )


class QAHistory(Base):
    """Q&A history model"""
    __tablename__ = "qa_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    context_used = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="qa_history")
    
    __table_args__ = (
        Index("idx_qa_history_project", "project_id"),
    )


class CodeEmbedding(Base):
    """Code embedding model for RAG"""
    __tablename__ = "code_embeddings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String, nullable=False)
    code_chunk = Column(Text, nullable=False)
    embedding = Column(Text, nullable=False)  # Stored as blob/text
    chunk_index = Column(Integer)
    
    # Relationships
    project = relationship("Project", back_populates="code_embeddings")


class TechDebt(Base):
    """Tech debt model"""
    __tablename__ = "tech_debt"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    file_path = Column(String)
    line_number = Column(Integer)
    severity = Column(String, nullable=False)
    category = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    estimated_effort = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="tech_debt")
    
    __table_args__ = (
        Index("idx_tech_debt_project", "project_id"),
        Index("idx_tech_debt_priority", "priority"),
    )


# Database initialization
def init_db():
    """Initialize database and create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()

# Made with Bob
