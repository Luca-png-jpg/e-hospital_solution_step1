from flask import Blueprint, request, jsonify, current_app
from src.virtualization.digital_replica.dr_factory import DRFactory

hospital_api = Blueprint("e_hospital_api", __name__, url_prefix="/api/hospital")


def register_e_hospital_blueprint(app):
    """Register the e-hospital blueprint with the Flask app"""
    app.register_blueprint(hospital_api)


# --- Room endpoints ---

@hospital_api.route("/rooms", methods=["POST"])
def create_room():
    """Create a new room DR"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        dr_factory = DRFactory("src/virtualization/templates/room.yaml")
        room = dr_factory.create_dr("room", data)

        room_number = room["profile"]["room_number"]
        existing = current_app.config["DB_SERVICE"].query_drs(
            "room", {"profile.room_number": room_number}
        )
        if existing:
            return jsonify({"error": f"Room {room_number} already exists"}), 409

        dr_id = current_app.config["DB_SERVICE"].save_dr("room", room)

        return jsonify({
            "status": "success",
            "message": "Room created successfully",
            "dr_id": dr_id,
            "room_number": room_number,
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@hospital_api.route("/rooms", methods=["GET"])
def list_rooms():
    """List all rooms with optional filters"""
    try:
        filters = {}
        if request.args.get("status"):
            filters["metadata.status"] = request.args.get("status")
        if request.args.get("room_type"):
            filters["profile.room_type"] = request.args.get("room_type")
        if request.args.get("floor") is not None:
            filters["profile.floor"] = int(request.args.get("floor"))

        rooms = current_app.config["DB_SERVICE"].query_drs("room", filters)
        return jsonify(rooms), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@hospital_api.route("/rooms/<room_number>", methods=["GET"])
def get_room(room_number):
    """Get room details"""
    try:
        room = current_app.config["DB_SERVICE"].query_drs("room", {"profile.room_number": room_number})
        if not room:
            return jsonify({"error": "Room not found"}), 404
        return jsonify(room), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Patient endpoints ---

@hospital_api.route("/patients", methods=["POST"])
def create_patient():
    """Create a new patient DR"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        dr_factory = DRFactory("src/virtualization/templates/patient.yaml")
        patient = dr_factory.create_dr("patient", data)

        clinical_id = patient["profile"]["patient_id"]
        existing = current_app.config["DB_SERVICE"].query_drs(
            "patient", {"profile.patient_id": clinical_id}
        )
        if existing:
            return jsonify({"error": f"Patient {clinical_id} already exists"}), 409

        dr_id = current_app.config["DB_SERVICE"].save_dr("patient", patient)

        return jsonify({
            "status": "success",
            "message": "Patient created successfully",
            "dr_id": dr_id,
            "patient_id": clinical_id,
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@hospital_api.route("/patients", methods=["GET"])
def list_patients():
    """List all patients with optional filters"""
    try:
        filters = {}
        if request.args.get("status"):
            filters["metadata.status"] = request.args.get("status")
        if request.args.get("patient_id"):
            filters["profile.patient_id"] = request.args.get("patient_id")

        patients = current_app.config["DB_SERVICE"].query_drs("patient", filters)
        return jsonify(patients), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@hospital_api.route("/patients/<patient_id>", methods=["GET"])
def get_patient(patient_id):
    """Get patient details"""
    try:
        patient = current_app.config["DB_SERVICE"].query_drs("patient", {"profile.patient_id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        return jsonify(patient), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Doctor endpoints ---

@hospital_api.route("/doctors", methods=["POST"])
def create_doctor():
    """Create a new doctor DR"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        dr_factory = DRFactory("src/virtualization/templates/doctor.yaml")
        doctor = dr_factory.create_dr("doctor", data)

        doctor_id = doctor["profile"]["doctor_id"]
        rfid_tag = doctor["profile"]["rfid_tag"]

        existing_id = current_app.config["DB_SERVICE"].query_drs(
            "doctor", {"profile.doctor_id": doctor_id}
        )
        if existing_id:
            return jsonify({"error": f"Doctor {doctor_id} already exists"}), 409

        existing_rfid = current_app.config["DB_SERVICE"].query_drs(
            "doctor", {"profile.rfid_tag": rfid_tag}
        )
        if existing_rfid:
            return jsonify({"error": f"RFID tag {rfid_tag} is already assigned"}), 409

        dr_id = current_app.config["DB_SERVICE"].save_dr("doctor", doctor)

        return jsonify({
            "status": "success",
            "message": "Doctor created successfully",
            "dr_id": dr_id,
            "doctor_id": doctor_id,
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@hospital_api.route("/doctors", methods=["GET"])
def list_doctors():
    """List all doctors with optional filters"""
    try:
        filters = {}
        if request.args.get("status"):
            filters["metadata.status"] = request.args.get("status")
        if request.args.get("specialization"):
            filters["profile.specialization"] = request.args.get("specialization")
        if request.args.get("rfid_tag"):
            filters["profile.rfid_tag"] = request.args.get("rfid_tag")

        doctors = current_app.config["DB_SERVICE"].query_drs("doctor", filters)
        return jsonify(doctors), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@hospital_api.route("/doctors/<doctor_id>", methods=["GET"])
def get_doctor(doctor_id):
    """Get doctor details"""
    try:
        doctor = current_app.config["DB_SERVICE"].query_drs("doctor", {"profile.doctor_id": doctor_id})
        if not doctor:
            return jsonify({"error": "Doctor not found"}), 404
        return jsonify(doctor), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500