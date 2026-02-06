"""
VWAP (Volume-Weighted Average Price) Execution Algorithm
Executes orders based on historical volume profile
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
import time


@dataclass
class VWAPOrder:
    """VWAP order configuration"""
    symbol: str
    side: str
    total_size: int
    volume_profile: pd.DataFrame  # Historical volume by time of day
    start_time: float
    executed_size: int = 0
    executed_value: float = 0.0
    status: str = "pending"


class VWAPExecutor:
    """
    Executes orders using VWAP algorithm
    """
    
    def __init__(self, api_client=None):
        self.api_client = api_client
        self.active_orders: Dict[str, VWAPOrder] = {}
    
    def create_volume_profile(
        self,
        historical_data: pd.DataFrame,
        time_bins: int = 60
    ) -> pd.DataFrame:
        """
        Create volume profile from historical data
        
        Args:
            historical_data: DataFrame with 'timestamp' and 'volume' columns
            time_bins: Number of time bins per day
        
        Returns:
            DataFrame with volume profile
        """
        # Extract time of day
        historical_data['time_of_day'] = pd.to_datetime(
            historical_data['timestamp'], unit='s'
        ).dt.time
        
        # Bin by time of day
        historical_data['time_bin'] = pd.cut(
            pd.to_datetime(historical_data['timestamp'], unit='s').dt.hour,
            bins=time_bins,
            labels=False
        )
        
        # Aggregate volume by time bin
        volume_profile = historical_data.groupby('time_bin')['volume'].mean().reset_index()
        volume_profile.columns = ['time_bin', 'avg_volume']
        
        # Normalize to percentages
        total_volume = volume_profile['avg_volume'].sum()
        volume_profile['volume_pct'] = volume_profile['avg_volume'] / total_volume
        
        return volume_profile
    
    def create_vwap_order(
        self,
        symbol: str,
        side: str,
        total_size: int,
        volume_profile: pd.DataFrame,
        duration_seconds: float
    ) -> str:
        """Create a VWAP order"""
        import uuid
        order_id = str(uuid.uuid4())
        
        order = VWAPOrder(
            symbol=symbol,
            side=side,
            total_size=total_size,
            volume_profile=volume_profile,
            start_time=time.time()
        )
        
        self.active_orders[order_id] = order
        return order_id
    
    def get_slice_size(self, order_id: str, current_time: float) -> int:
        """
        Calculate size for current time slice based on volume profile
        """
        if order_id not in self.active_orders:
            return 0
        
        order = self.active_orders[order_id]
        
        # Get current time of day (hour)
        from datetime import datetime
        current_hour = datetime.fromtimestamp(current_time).hour
        
        # Find corresponding volume bin
        time_bins = len(order.volume_profile)
        bin_idx = int((current_hour / 24) * time_bins)
        bin_idx = min(bin_idx, time_bins - 1)
        
        # Get volume percentage for this bin
        volume_pct = order.volume_profile.iloc[bin_idx]['volume_pct']
        
        # Calculate target execution for this bin
        target_for_bin = order.total_size * volume_pct
        
        # Calculate how much should be executed by now
        elapsed = current_time - order.start_time
        # Assume 1-hour bins for simplicity
        bin_duration = 3600  # 1 hour in seconds
        current_bin_progress = (elapsed % bin_duration) / bin_duration
        
        target_executed_in_bin = target_for_bin * current_bin_progress
        
        # Total target executed
        bins_completed = int(elapsed / bin_duration)
        target_total = sum(
            order.volume_profile.iloc[i]['volume_pct'] * order.total_size
            for i in range(min(bins_completed, len(order.volume_profile)))
        ) + target_executed_in_bin
        
        # Size for this slice
        slice_size = int(target_total) - order.executed_size
        
        return max(0, slice_size)
    
    async def execute_slice(self, order_id: str, current_time: float) -> Dict:
        """Execute one time slice of VWAP order"""
        if order_id not in self.active_orders:
            return {"error": "Order not found"}
        
        order = self.active_orders[order_id]
        slice_size = self.get_slice_size(order_id, current_time)
        
        if slice_size > 0 and self.api_client:
            # Execute slice
            executed = slice_size
            avg_price = 100.0  # Would get from execution
            
            order.executed_size += executed
            order.executed_value += executed * avg_price
            
            if order.executed_size >= order.total_size:
                order.status = "completed"
            
            return {
                "status": "executing",
                "slice_size": executed,
                "total_executed": order.executed_size
            }
        
        return {"status": "waiting"}
