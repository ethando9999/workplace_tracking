from qdrant_client import QdrantClient
from typing import Optional, Union, Callable, Awaitable, Any


class QdrantConfig:
    """
    This class manages the basic configuration for the Qdrant client,
    handling options for local or remote connections.
    """

    def __init__(
        self,
        location: Optional[str] = None,
        https: Optional[bool] = None,
        api_key: Optional[str] = None,
        host: Optional[str] = None,
        path: Optional[str] = None,
        force_disable_check_same_thread: bool = False,
        auth_token_provider: Optional[Union[Callable[[], str], Callable[[], Awaitable[str]]]] = None,
        **kwargs: Any,
    ):
        # Save essential initialization parameters
        self.location = location
        self.https = https
        self.api_key = api_key
        self.host = host
        self.path = path
        self.force_disable_check_same_thread = force_disable_check_same_thread
        self.auth_token_provider = auth_token_provider

        # Validate that only one of the location, host, or path is set
        if sum([param is not None for param in (location, host, path)]) > 1:
            raise ValueError("Only one of <location>, <host>, or <path> should be specified.")


class QdrantConnection:
    """
    This class establishes a connection to Qdrant, supporting both local and remote instances.
    """

    def __init__(self, config: QdrantConfig):
        self._config = config
        self._client = self._connect()

    def _connect(self):
        # Select the connection type based on the configuration
        if self._config.location == ":memory:":
            return QdrantClient(
                location=self._config.location,
                force_disable_check_same_thread=self._config.force_disable_check_same_thread
            )
        elif self._config.path is not None:
            return QdrantClient(
                location=self._config.path,
                force_disable_check_same_thread=self._config.force_disable_check_same_thread
            )
        else:
            return QdrantClient(
                url=self._config.host,
                https=self._config.https,
                api_key=self._config.api_key,
                auth_token_provider=self._config.auth_token_provider,
            )

    def close(self):
        """Close the Qdrant client connection."""
        if self._client:
            self._client.close()
            print("Qdrant connection closed.")

    def get_client(self):
        """Return the Qdrant client instance."""
        return self._client

    def __del__(self):
        self.close()
