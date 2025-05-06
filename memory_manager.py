from zep_python import ZepClient
from typing import Dict, Any
import json
import os
from dotenv import load_dotenv

load_dotenv()

class MemoryManager:
    def __init__(self):
        self.zep_client = ZepClient(
            base_url=os.getenv("ZEP_API_URL", "https://api.zep.cloud"),
            api_key=os.getenv("ZEP_API_KEY")
        )
        self.collection_name = "user_memory"
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        try:
            self.zep_client.document.get_collection(self.collection_name)
        except Exception as e:
            print(f"Error accessing collection: {e}")
            # Create collection if it doesn't exist
            try:
                self.zep_client.document.add_collection(
                    name=self.collection_name,
                    description="User memory storage",
                    metadata={"type": "user_memory"}
                )
            except Exception as e:
                print(f"Error creating collection: {e}")
                raise

    def store_memory(self, user_id: str, memory_data: Dict[str, Any]):
        """Store a memory about the user"""
        try:
            document = {
                "content": json.dumps(memory_data),
                "metadata": {
                    "user_id": user_id,
                    "type": "user_memory"
                }
            }
            self.zep_client.document.add(
                collection_name=self.collection_name,
                documents=[document]
            )
        except Exception as e:
            print(f"Error storing memory: {e}")
            raise

    def get_memories(self, user_id: str) -> Dict[str, Any]:
        """Retrieve all memories for a user"""
        try:
            search_results = self.zep_client.document.search(
                collection_name=self.collection_name,
                search_params={
                    "metadata": {
                        "user_id": user_id,
                        "type": "user_memory"
                    }
                }
            )
            
            memories = {}
            for result in search_results:
                try:
                    memory_data = json.loads(result.content)
                    memories.update(memory_data)
                except Exception as e:
                    print(f"Error parsing memory data: {e}")
                    continue
            return memories
        except Exception as e:
            print(f"Error retrieving memories: {e}")
            return {}

    def update_memory(self, user_id: str, key: str, value: Any):
        """Update a specific memory for a user"""
        try:
            memories = self.get_memories(user_id)
            memories[key] = value
            self.store_memory(user_id, memories)
        except Exception as e:
            print(f"Error updating memory: {e}")
            raise

    def clear_memories(self, user_id: str):
        """Clear all memories for a user"""
        try:
            self.zep_client.document.delete(
                collection_name=self.collection_name,
                metadata={
                    "user_id": user_id,
                    "type": "user_memory"
                }
            )
        except Exception as e:
            print(f"Error clearing memories: {e}")
            raise 