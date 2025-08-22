from datetime import datetime
from enum import Enum
from eralchemy import render_er

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    String,
    Boolean,
    Integer,
    DateTime,
    Text,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class PrivacyEnum(Enum):
    PUBLICO = "publico"
    SEGUIDORES = "seguidores"
    PRIVADO = "privado"

class User(db.Model):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(150))
    bio: Mapped[str] = mapped_column(Text)
    website: Mapped[str] = mapped_column(String(255))
    is_private: Mapped[bool] = mapped_column(Boolean(), default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean(), default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    posts = relationship("Publicacion", back_populates="autor", cascade="all, delete-orphan")
    medios = relationship("Medio", back_populates="owner", cascade="all, delete-orphan")
    comentarios = relationship("Comentario", back_populates="autor", cascade="all, delete-orphan")
    seguidores_rel = relationship(
        "Seguidores",
        foreign_keys="Seguidores.id_seguido",
        back_populates="seguido",
        cascade="all, delete-orphan",
    )
    siguiendo_rel = relationship(
        "Seguidores",
        foreign_keys="Seguidores.id_seguidor",
        back_populates="seguidor",
        cascade="all, delete-orphan",
    )

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "bio": self.bio,
            "website": self.website,
            "is_private": bool(self.is_private),
            "is_verified": bool(self.is_verified),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<User {self.id} {self.username}>"


class Publicacion(db.Model):
    __tablename__ = "publicacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_usuario: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False, index=True)
    texto: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    privacy: Mapped[str] = mapped_column(String(20), default=PrivacyEnum.PUBLICO.value, nullable=False)
    location: Mapped[str] = mapped_column(String(255))
    like_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean(), default=False, nullable=False)


    autor = relationship("User", back_populates="posts")
    medios = relationship("Medio", back_populates="publicacion", cascade="all, delete-orphan")
    comentarios = relationship("Comentario", back_populates="publicacion", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "id_usuario": self.id_usuario,
            "texto": self.texto,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "privacy": self.privacy,
            "location": self.location,
            "like_count": self.like_count,
            "comment_count": self.comment_count,
            "medios": [m.serialize() for m in self.medios],
        }

    def __repr__(self):
        return f"<Publicacion {self.id} by {self.id_usuario}>"


class Medio(db.Model):
    __tablename__ = "medio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_usuario: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.id", ondelete="SET NULL"), nullable=True, index=True)
    id_pub: Mapped[int] = mapped_column(Integer, ForeignKey("publicacion.id", ondelete="CASCADE"), nullable=True, index=True)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    media_type: Mapped[str] = mapped_column(String(20), nullable=False)  
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="medios")
    publicacion = relationship("Publicacion", back_populates="medios")

    def serialize(self):
        return {
            "id": self.id,
            "id_usuario": self.id_usuario,
            "id_pub": self.id_pub,
            "url": self.url,
            "media_type": self.media_type,
            "width": self.width,
            "height": self.height,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Medio {self.id} ({self.media_type})>"


class Comentario(db.Model):
    __tablename__ = "comentarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_pub: Mapped[int] = mapped_column(Integer, ForeignKey("publicacion.id", ondelete="CASCADE"), nullable=False, index=True)
    id_usuario: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False, index=True)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    parent_comment_id: Mapped[int] = mapped_column(Integer, ForeignKey("comentarios.id", ondelete="CASCADE"), nullable=True)

   
    publicacion = relationship("Publicacion", back_populates="comentarios")
    autor = relationship("User", back_populates="comentarios")
    replies = relationship("Comentario", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "id_pub": self.id_pub,
            "id_usuario": self.id_usuario,
            "texto": self.texto,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "parent_comment_id": self.parent_comment_id,
        }

    def __repr__(self):
        return f"<Comentario {self.id} on pub {self.id_pub}>"


class Seguidores(db.Model):
    __tablename__ = "seguidores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_seguidor: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False)
    id_seguido: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)

    seguidor = relationship("User", foreign_keys=[id_seguidor], back_populates="siguiendo_rel")
    seguido = relationship("User", foreign_keys=[id_seguido], back_populates="seguidores_rel")

    __table_args__ = (UniqueConstraint("id_seguidor", "id_seguido", name="uix_seguidor_seguido"),)

    def serialize(self):
        return {
            "id": self.id,
            "id_seguidor": self.id_seguidor,
            "id_seguido": self.id_seguido,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": bool(self.is_active),
        }

    def __repr__(self):
        return f"<Seguidores {self.id_seguidor} -> {self.id_seguido}>"
    
    
try:
    
    result = render_er(db.Model, 'diagram.png')
    print("diagrama generado exitosamente: diagram.png")
except Exception as e:
    print("hubo un problema al generar el diagrama:", e)
