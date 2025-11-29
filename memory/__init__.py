"""
Memory and session management for the Financial Agent System.

Provides session state management and long-term memory capabilities
using ADK's session and memory services.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService

from config import config
from observability.logging_config import get_logger

logger = get_logger(__name__)


class FinancialMemoryService:
    """
    Custom memory service for financial data persistence.
    
    Extends ADK's memory capabilities with:
    - User preference storage
    - Portfolio history tracking
    - Analysis result caching
    """
    
    def __init__(self):
        """Initialize memory service."""
        self._session_service = InMemorySessionService()
        self._memory_service = InMemoryMemoryService()
        
        # Custom storage for financial-specific data
        self._user_preferences: Dict[str, Dict[str, Any]] = {}
        self._portfolio_history: Dict[str, List[Dict[str, Any]]] = {}
        self._analysis_cache: Dict[str, Dict[str, Any]] = {}
    
    @property
    def session_service(self) -> InMemorySessionService:
        """Get the underlying session service."""
        return self._session_service
    
    @property
    def memory_service(self) -> InMemoryMemoryService:
        """Get the underlying memory service."""
        return self._memory_service
    
    async def create_session(
        self,
        user_id: str,
        session_id: str,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Create a new session for a user.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            initial_state: Optional initial state values
        """
        state = initial_state or {}
        
        # Add user preferences if available
        if user_id in self._user_preferences:
            state["user:preferences"] = self._user_preferences[user_id]
        
        await self._session_service.create_session(
            app_name=config.APP_NAME,
            user_id=user_id,
            session_id=session_id,
            state=state
        )
        
        logger.info(f"Created session {session_id} for user {user_id}")
    
    async def get_session(self, user_id: str, session_id: str):
        """Get an existing session."""
        return await self._session_service.get_session(
            app_name=config.APP_NAME,
            user_id=user_id,
            session_id=session_id
        )
    
    async def update_session_state(
        self,
        user_id: str,
        session_id: str,
        updates: Dict[str, Any]
    ) -> None:
        """
        Update session state values.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            updates: State updates to apply
        """
        session = await self.get_session(user_id, session_id)
        if session:
            for key, value in updates.items():
                session.state[key] = value
            logger.debug(f"Updated session state: {list(updates.keys())}")
    
    def set_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> None:
        """
        Set user preferences for personalization.
        
        Args:
            user_id: User identifier
            preferences: Preference settings
        """
        self._user_preferences[user_id] = {
            **self._user_preferences.get(user_id, {}),
            **preferences,
            "updated_at": datetime.now().isoformat()
        }
        logger.info(f"Updated preferences for user {user_id}")
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences."""
        return self._user_preferences.get(user_id)
    
    def save_portfolio_snapshot(
        self,
        user_id: str,
        holdings: Dict[str, float],
        analysis_result: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Save a portfolio snapshot to history.
        
        Args:
            user_id: User identifier
            holdings: Portfolio holdings
            analysis_result: Optional analysis results
        """
        if user_id not in self._portfolio_history:
            self._portfolio_history[user_id] = []
        
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "holdings": holdings,
            "analysis": analysis_result,
        }
        
        self._portfolio_history[user_id].append(snapshot)
        
        # Keep only last N snapshots
        max_history = config.MAX_MEMORY_ITEMS
        if len(self._portfolio_history[user_id]) > max_history:
            self._portfolio_history[user_id] = self._portfolio_history[user_id][-max_history:]
        
        logger.info(f"Saved portfolio snapshot for user {user_id}")
    
    def get_portfolio_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get portfolio history for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of snapshots to return
        
        Returns:
            List of portfolio snapshots
        """
        history = self._portfolio_history.get(user_id, [])
        return history[-limit:]
    
    def cache_analysis(
        self,
        cache_key: str,
        analysis_data: Dict[str, Any],
        ttl_minutes: int = 30
    ) -> None:
        """
        Cache analysis results.
        
        Args:
            cache_key: Unique cache key
            analysis_data: Analysis data to cache
            ttl_minutes: Time-to-live in minutes
        """
        self._analysis_cache[cache_key] = {
            "data": analysis_data,
            "cached_at": datetime.now().isoformat(),
            "ttl_minutes": ttl_minutes
        }
    
    def get_cached_analysis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached analysis if still valid.
        
        Args:
            cache_key: Cache key to look up
        
        Returns:
            Cached data if valid, None otherwise
        """
        cached = self._analysis_cache.get(cache_key)
        if not cached:
            return None
        
        # Check TTL
        cached_at = datetime.fromisoformat(cached["cached_at"])
        ttl = cached["ttl_minutes"]
        
        from datetime import timedelta
        if datetime.now() - cached_at > timedelta(minutes=ttl):
            # Expired
            del self._analysis_cache[cache_key]
            return None
        
        return cached["data"]
    
    async def add_to_memory(
        self,
        user_id: str,
        session_id: str,
        key: str,
        content: str
    ) -> None:
        """
        Add content to long-term memory.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            key: Memory key/topic
            content: Content to remember
        """
        # Store in memory service
        session = await self.get_session(user_id, session_id)
        if session:
            await self._memory_service.add_session_to_memory(session)
            logger.info(f"Added session to memory for user {user_id}")
    
    async def search_memory(
        self,
        user_id: str,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search long-term memory.
        
        Args:
            user_id: User identifier
            query: Search query
            limit: Maximum results
        
        Returns:
            List of relevant memory items
        """
        result = await self._memory_service.search_memory(
            app_name=config.APP_NAME,
            user_id=user_id,
            query=query
        )
        
        # Format results
        items = []
        if result and result.memories:
            for memory in result.memories[:limit]:
                items.append({
                    "content": str(memory),
                    "relevance": "high"  # Simplified
                })
        
        return items


# Global instance
memory_service = FinancialMemoryService()


async def auto_save_memory_callback(callback_context):
    """
    Callback to automatically save important information to memory.
    
    This can be attached to agents to persist analysis results.
    """
    # Check if there's analysis to save
    state = callback_context.state
    
    # Save portfolio analysis if present
    if "portfolio_analysis_result" in state:
        user_id = state.get("user_id", "default")
        holdings = state.get("portfolio_holdings", {})
        
        memory_service.save_portfolio_snapshot(
            user_id=user_id,
            holdings=holdings,
            analysis_result=state["portfolio_analysis_result"]
        )
    
    # Cache expensive analysis results
    if "performance_evaluation_result" in state:
        cache_key = f"{state.get('user_id', 'default')}:performance"
        memory_service.cache_analysis(
            cache_key=cache_key,
            analysis_data=state["performance_evaluation_result"],
            ttl_minutes=30
        )


"""
Usage Example:

from memory.memory_service import memory_service

# Create a session
await memory_service.create_session(
    user_id="user123",
    session_id="sess456",
    initial_state={"portfolio_holdings": {"AAPL": 40, "GOOGL": 30}}
)

# Set user preferences
memory_service.set_user_preferences(
    user_id="user123",
    preferences={
        "risk_tolerance": "moderate",
        "investment_horizon": 10,
        "preferred_sectors": ["Technology", "Healthcare"]
    }
)

# Save portfolio snapshot
memory_service.save_portfolio_snapshot(
    user_id="user123",
    holdings={"AAPL": 40, "GOOGL": 30, "MSFT": 20, "CASH": 10},
    analysis_result={"diversification_score": 75}
)

# Get portfolio history
history = memory_service.get_portfolio_history("user123", limit=5)

# Search memory
results = await memory_service.search_memory(
    user_id="user123",
    query="risk assessment"
)
"""
