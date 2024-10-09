import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import json
import os


class FirebaseDBManager:
    def __init__(self):
        cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), 'firebase_creds.json'))
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

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
