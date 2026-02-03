from shepard_client.api_client import ApiClient
from shepard_client.configuration import Configuration
from shepard_client.api.collection_api import CollectionApi
from shepard_client.api.data_object_api import DataObjectApi
from shepard_client.models.collection import Collection
from shepard_client.models.data_object import DataObject
from dotenv import load_dotenv
import os

from taipy.gui import notify
from utils.logger import logger

load_dotenv()


class ShepardManager:
    """Manages ShepardDB connections and data operations using Keycloak token authentication."""
    
    def __init__(self, access_token=None):
        """
        Initialize ShepardDB client with Keycloak access token.
        
        Args:
            access_token (str, optional): Keycloak access token for authentication
        """
        self.host = os.getenv("SHEPARD_HOST")
        
        if not self.host:
            raise ValueError("SHEPARD_HOST must be set in environment")
        
        self.access_token = access_token
        self.client = None
        self.collection_api = None
        self.dataobject_api = None
        
        if access_token:
            self._initialize_client(access_token)
    
    def _initialize_client(self, access_token):
        """
        Initialize the ShepardDB client with the provided access token.
        
        Args:
            access_token (str): Keycloak access token
        """
        self.access_token = access_token
        
        # Set up configuration with bearer token
        conf = Configuration(
            host=self.host,
            access_token=access_token
        )
        self.client = ApiClient(configuration=conf)
        
        # Initialize API instances
        self.collection_api = CollectionApi(self.client)
        self.dataobject_api = DataObjectApi(self.client)
    
    def set_access_token(self, access_token):
        """
        Update the access token and reinitialize the client.
        
        Args:
            access_token (str): New Keycloak access token
        """
        self._initialize_client(access_token)
    
    def is_authenticated(self):
        """
        Check if the manager has a valid client connection.
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.client is not None and self.access_token is not None
    
    # Collection Methods
    
    def get_all_collections(self):
        """
        Retrieve all collections.
        
        Returns:
            list: List of all collections or None if error
        """
        if not self.is_authenticated():
            logger.error("Error: Not authenticated. Please set access token first.")
            return None
        
        try:
            collections = self.collection_api.get_all_collections()
            return collections
        except Exception as e:
            logger.error(f"Error retrieving collections: {str(e)}")
            return None
    
    def get_collection_by_id(self, collection_id):
        """
        Retrieve a specific collection by ID.
        
        Args:
            collection_id (str): The collection ID
            
        Returns:
            Collection: The collection object or None if error
        """
        if not self.is_authenticated():
            logger.error("Error: Not authenticated. Please set access token first.")
            return None
        
        try:
            collection = self.collection_api.get_collection(collection_id=collection_id)
            return collection
        except Exception as e:
            logger.error(f"Error retrieving collection {collection_id}: {str(e)}")
            return None
    
    def create_collection(self, name, description, attributes=None):
        """
        Create a new collection.
        
        Args:
            name (str): Collection name
            description (str): Collection description
            attributes (dict, optional): Custom attributes as key-value pairs
            
        Returns:
            Collection: The created collection or None if error
        """
        if not self.is_authenticated():
            logger.error("Error: Not authenticated. Please set access token first.")
            return None
        
        try:
            collection_to_create = Collection(
                name=name,
                description=description,
                attributes=attributes or {}
            )
            created_collection = self.collection_api.create_collection(
                collection=collection_to_create
            )
            return created_collection
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            return None
    
    def update_collection(self, collection_id, name=None, description=None, attributes=None):
        """
        Update an existing collection.
        
        Args:
            collection_id (str): The collection ID
            name (str, optional): New collection name
            description (str, optional): New collection description
            attributes (dict, optional): New custom attributes
            
        Returns:
            Collection: The updated collection or None if error
        """
        if not self.is_authenticated():
            logger.error("Error: Not authenticated. Please set access token first.")
            return None
        
        try:
            # Get existing collection first
            existing_collection = self.get_collection_by_id(collection_id)
            if not existing_collection:
                return None
            
            # Update only provided fields
            if name:
                existing_collection.name = name
            if description:
                existing_collection.description = description
            if attributes is not None:
                existing_collection.attributes = attributes
            
            updated_collection = self.collection_api.update_collection(
                collection_id=collection_id,
                collection=existing_collection
            )
            return updated_collection
        except Exception as e:
            logger.error(f"Error updating collection {collection_id}: {str(e)}")
            return None
    
    def delete_collection(self, collection_id):
        """
        Delete a collection.
        
        Args:
            collection_id (str): The collection ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_authenticated():
            logger.error("Error: Not authenticated. Please set access token first.")
            return False
        
        try:
            self.collection_api.delete_collection(collection_id=collection_id)
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {collection_id}: {str(e)}")
            return False
    
    # Data Object Methods
    
    def get_all_data_objects(self, collection_id):
        """
        Retrieve all data objects in a collection.
        
        Args:
            collection_id (str): The collection ID
            
        Returns:
            list: List of all data objects in the collection or None if error
        """
        if not self.is_authenticated():
            print("Error: Not authenticated. Please set access token first.")
            return None
        
        try:
            data_objects = self.dataobject_api.get_all_data_objects(
                collection_id=collection_id
            )
            return data_objects
        except Exception as e:
            print(f"Error retrieving data objects: {str(e)}")
            return None
    
    def get_data_object(self, collection_id, data_object_id):
        """
        Retrieve a specific data object.
        
        Args:
            collection_id (str): The collection ID
            data_object_id (str): The data object ID
            
        Returns:
            DataObject: The data object or None if error
        """
        if not self.is_authenticated():
            logger.error("Error: Not authenticated. Please set access token first.")
            return None
        
        try:
            data_object = self.dataobject_api.get_data_object(
                collection_id=collection_id,
                data_object_id=data_object_id
            )
            return data_object
        except Exception as e:
            logger.error(f"Error retrieving data object {data_object_id}: {str(e)}")
            return None
    
    def create_data_object(self, collection_id, name, description, parent_id=None, predecessor_ids=None):
        """
        Create a new data object in a collection.
        
        Args:
            collection_id (str): The collection ID
            name (str): Data object name
            description (str): Data object description
            parent_id (str, optional): Parent data object ID
            predecessor_ids (list, optional): List of predecessor data object IDs
            
        Returns:
            DataObject: The created data object or None if error
        """
        if not self.is_authenticated():
            logger.error("Error: Not authenticated. Please set access token first.")
            return None
        
        try:
            dataobject_to_create = DataObject(
                name=name,
                description=description,
                parentId=parent_id,
                predecessorIds=predecessor_ids or []
            )
            created_dataobject = self.dataobject_api.create_data_object(
                collection_id=collection_id,
                data_object=dataobject_to_create
            )
            return created_dataobject
        except Exception as e:
            logger.error(f"Error creating data object: {str(e)}")
            return None
    
    def update_data_object(self, collection_id, data_object_id, name=None, description=None, parent_id=None, predecessor_ids=None):
        """
        Update an existing data object.
        
        Args:
            collection_id (str): The collection ID
            data_object_id (str): The data object ID
            name (str, optional): New data object name
            description (str, optional): New data object description
            parent_id (str, optional): New parent data object ID
            predecessor_ids (list, optional): New list of predecessor data object IDs
            
        Returns:
            DataObject: The updated data object or None if error
        """
        if not self.is_authenticated():
            logger.error("Error: Not authenticated. Please set access token first.")
            return None
        
        try:
            # Get existing data object first
            existing_dataobject = self.get_data_object(collection_id, data_object_id)
            if not existing_dataobject:
                return None
            
            # Update only provided fields
            if name:
                existing_dataobject.name = name
            if description:
                existing_dataobject.description = description
            if parent_id is not None:
                existing_dataobject.parentId = parent_id
            if predecessor_ids is not None:
                existing_dataobject.predecessorIds = predecessor_ids
            
            updated_dataobject = self.dataobject_api.update_data_object(
                collection_id=collection_id,
                data_object_id=data_object_id,
                data_object=existing_dataobject
            )
            return updated_dataobject
        except Exception as e:
            logger.error(f"Error updating data object {data_object_id}: {str(e)}")
            return None
    
    def delete_data_object(self, collection_id, data_object_id):
        """
        Delete a data object.
        
        Args:
            collection_id (str): The collection ID
            data_object_id (str): The data object ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_authenticated():
            logger.error("Error: Not authenticated. Please set access token first.")
            return False
        
        try:
            self.dataobject_api.delete_data_object(
                collection_id=collection_id,
                data_object_id=data_object_id
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting data object {data_object_id}: {str(e)}")
            return False
        
    def build_tree_structure(self):
        """
        Build a Taipy-compatible tree with infinite hierarchical depth,
        adding a 'path' key for each node to trace full parent path.
        Also prints DataObject attributes for debugging parent field.
        """
        logger.info("Building tree structure from ShepardDB")

        collections = self.get_all_collections()
        if collections is None:
            logger.error("Failed to retrieve collections!")
            return []

        tree_data = []

        def build_dataobject_tree(objects, parent_id=None, parent_path=""):
            """Recursively build a nested tree of data objects with parent path."""
            children = []

            for obj in objects:

                # === Determine parent ID dynamically ===
                obj_parent_id = getattr(obj, "parentId", None) or getattr(obj, "parent_id", None)

                if obj_parent_id == parent_id:
                    current_path = f"{parent_path} → {obj.name}" if parent_path else obj.name
                    node = {
                        "id": obj.id,
                        "label": obj.name,
                        "children": build_dataobject_tree(objects, parent_id=obj.id, parent_path=current_path),
                        "type": "data_object",
                        "path": current_path
                    }
                    children.append(node)

            return children

        # Build tree for each collection
        for col in collections:
            logger.info(f"Processing collection: {col.name}")

            data_objects = self.get_all_data_objects(col.id)
            if data_objects is None:
                data_objects = []

            # Root path starts with collection name
            hierarchy = build_dataobject_tree(data_objects, parent_id=None, parent_path=col.name)

            tree_data.append({
                "id": col.id,
                "label": col.name,
                "children": hierarchy,
                "type": "collection",
                "path": col.name
            })

        return tree_data

    
