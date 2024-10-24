import os
import firebase_admin
from firebase_admin import credentials, firestore
import json

cred = credentials.Certificate(
    os.path.join(os.path.dirname(__file__), "firebase_creds.json")
)
firebase_admin.initialize_app(cred)
db = firestore.client()


def get_user_feedback(user_id):
    user_ref = db.collection("feedback").document(user_id)
    user_doc = user_ref.get()
    if user_doc.exists:
        return user_doc.to_dict().get("feedback")
    else:
        return None


if __name__ == "__main__":
    user_id = input("Enter the user ID: ")
    file_name = input("File name: ")
    feedback = get_user_feedback(user_id)
    if feedback:
        with open(file_name + ".json", "w") as f:
            json.dump(feedback, f, indent=4)
    else:
        print(f"No feedback found for user {user_id}")
