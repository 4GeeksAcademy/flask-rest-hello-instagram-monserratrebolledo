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
    correo: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    telefono: Mapped[str] = mapped_column(String(30))
    nombre: Mapped[str] = mapped_column(String(80), nullable=False)
    apellido: Mapped[str] = mapped_column(String(80), nullable=False)


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
            "correo": self.correo,
            "telefono": self.telefono,
            "nombre": self.nombre,
            "apellido": self.apellido,
        }

    def __repr__(self):
        return f"<User {self.id} {self.correo}>"


class Publicacion(db.Model):
    __tablename__ = "publicacion"

   
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_usuario: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False, index=True)
    texto: Mapped[str] = mapped_column(Text)
   
    fecha_pub: Mapped[str] = mapped_column(String(10))  
    hora_pub: Mapped[str] = mapped_column(String(8))    

    autor = relationship("User", back_populates="posts")
    medios = relationship("Medio", back_populates="publicacion", cascade="all, delete-orphan")
    comentarios = relationship("Comentario", back_populates="publicacion", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "id_usuario": self.id_usuario,
            "texto": self.texto,
            "fecha_pub": self.fecha_pub,
            "hora_pub": self.hora_pub,
        }

    def __repr__(self):
        return f"<Publicacion {self.id} by {self.id_usuario}>"


class Medio(db.Model):
    __tablename__ = "medio"

    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    tipo_archiv: Mapped[str] = mapped_column(String(50), nullable=False)  
    id_pub: Mapped[int] = mapped_column(Integer, ForeignKey("publicacion.id", ondelete="CASCADE"), nullable=True, index=True)
   
    id_usuario: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.id", ondelete="SET NULL"), nullable=True, index=True)

    owner = relationship("User", back_populates="medios", foreign_keys=[id_usuario])
    publicacion = relationship("Publicacion", back_populates="medios", foreign_keys=[id_pub])

    def serialize(self):
        return {
            "id": self.id,
            "url": self.url,
            "tipo_archiv": self.tipo_archiv,
            "id_pub": self.id_pub,
            "id_usuario": self.id_usuario,
        }

    def __repr__(self):
        return f"<Medio {self.id} ({self.tipo_archiv})>"


class Comentario(db.Model):
    __tablename__ = "comentarios"

   
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_pub: Mapped[int] = mapped_column(Integer, ForeignKey("publicacion.id", ondelete="CASCADE"), nullable=False, index=True)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    fecha: Mapped[str] = mapped_column(String(10)) 
    hora: Mapped[str] = mapped_column(String(8))    
    id_usuario: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_comment_id: Mapped[int] = mapped_column(Integer, ForeignKey("comentarios.id", ondelete="CASCADE"), nullable=True)

    publicacion = relationship("Publicacion", back_populates="comentarios", foreign_keys=[id_pub])
    autor = relationship("User", back_populates="comentarios", foreign_keys=[id_usuario])
    replies = relationship("Comentario", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "id_pub": self.id_pub,
            "texto": self.texto,
            "fecha": self.fecha,
            "hora": self.hora,
            "id_usuario": self.id_usuario,
            "parent_comment_id": self.parent_comment_id,
        }

    def __repr__(self):
        return f"<Comentario {self.id} on pub {self.id_pub}>"


class Seguidores(db.Model):
    __tablename__ = "seguidores"

    o
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