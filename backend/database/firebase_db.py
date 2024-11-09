import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone
import json
import os
import pytz


cred = credentials.Certificate(
    os.path.join(os.path.dirname(__file__), "firebase_creds.json")
)
firebase_admin.initialize_app(cred)


class FirebaseDBManager:
    def __init__(self):
        self.db = firestore.client()

    def send_feedback(self, user_id, feedback):
        print("uploading feedback", feedback)
        doc_ref = self.db.collection("feedback").document(user_id)
        doc = doc_ref.get()
        if not doc.exists or "feedback" not in doc.to_dict():
            doc_ref.set({"feedback": []})
        doc_ref.update(
            {
                "feedback": firestore.ArrayUnion(
                    [
                        {
                            "feedback": feedback,
                            "timestamp": datetime.now(
                                pytz.timezone("America/Los_Angeles")
                            ).strftime("%Y-%m-%d %I:%M:%S %p %Z"),
                        }
                    ]
                )
            }
        )

    def store_analytics(self, event):
        """
        Stores analytics events in Firebase under the cuj_id document.
        Each document contains user_id and events mapping.
        """
        print(f"Storing analytics event: {event}")
        doc_ref = self.db.collection("latency_analytics").document(event.cuj_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            # Create new document if it doesn't exist
            doc_ref.set({
                "user_id": event.user_id,
                "events": {event.event_type: event.timestamp}
            })
        else:
            # Update existing document with new event
            doc_ref.update({
                f"events.{event.event_type}": event.timestamp
            })

    def _get_user_doc(self, user_id):
        return self.db.collection("users").document(user_id)

    def create_or_get_user(self, user_id, default_data):
        doc_ref = self._get_user_doc(user_id)
        doc = doc_ref.get()
        if not doc.exists:
            doc_ref.set(default_data)
            return default_data
        return doc.to_dict()

    def update_user_field(self, user_id, field, data):
        """
        Updates a specific field (chat, events, or todo) for the given user in Firebase.
        """
        doc_ref = self._get_user_doc(user_id)
        doc_ref.update({field: data})

    def append_to_array_field(self, user_id, field, data):
        """
        Append an element to an array field in Firebase (e.g., chat, events, or todo).
        """
        doc_ref = self._get_user_doc(user_id)
        doc_ref.update({field: firestore.ArrayUnion([data])})

    def batch_update(self, user_id, data_updates):
        """
        Updates multiple fields in Firebase in a single batch operation.
        """
        doc_ref = self._get_user_doc(user_id)
        batch = self.db.batch()
        for field, data in data_updates.items():
            batch.update(doc_ref, {field: data})
        batch.commit()
