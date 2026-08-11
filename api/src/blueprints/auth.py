"""Authentication blueprint — register, login, token management."""

from flask import Blueprint, request, jsonify
from sqlalchemy import select

from src.database import get_db
from src.models import User
from src.auth import create_access_token, get_password_hash, verify_password

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    db = get_db()
    try:
        existing = db.query(User).filter(User.email == data["email"]).first()
        if existing:
            return jsonify({
                "status": "error",
                "error_type": "conflict",
                "message": "Email already registered",
            }), 409

        user = User(email=data["email"], password_hash=get_password_hash(data["password"]))
        db.add(user)
        db.commit()
        db.refresh(user)
        return jsonify({
            "status": "ok",
            "data": {
                "id": user.id,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
            },
        }), 201
    finally:
        db.close()


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    db = get_db()
    try:
        user = db.query(User).filter(User.email == data["email"]).first()
        if not user or not verify_password(data["password"], user.password_hash):
            return jsonify({
                "status": "error",
                "error_type": "invalid_credentials",
                "message": "Invalid email or password",
            }), 401

        token = create_access_token({"sub": str(user.id)})
        return jsonify({
            "status": "ok",
            "data": {
                "access_token": token,
                "token_type": "bearer",
            },
        })
    finally:
        db.close()
