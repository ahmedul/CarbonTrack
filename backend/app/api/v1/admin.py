"""
Admin API endpoints for CarbonTrack
Handles admin-only operations like user management, stats, etc.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, List, Any, Optional
import boto3
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.middleware import get_current_user
from app.core.config import settings

router = APIRouter(prefix="/admin", tags=["Admin"])


def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Dependency to ensure only admin users can access these endpoints"""
    # For demo/mock users, allow admin access for testing
    if current_user.get("user_id", "").startswith(("mock_", "demo-", "test_")):
        return current_user
    
    # Check if user has admin role in real authentication
    if current_user.get("email") == "ahmedulkabir55@gmail.com":
        return current_user
    
    # Could also check user role from database here
    dynamodb = boto3.resource('dynamodb', region_name=settings.aws_region)
    users_table = dynamodb.Table(settings.users_table)
    
    try:
        response = users_table.get_item(Key={'userId': current_user.get('user_id')})
        user = response.get('Item', {})
        if user.get('role') != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return current_user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


@router.get("/users")
async def get_all_users(admin_user: Dict[str, Any] = Depends(require_admin)) -> Dict[str, Any]:
    """Get list of all users (admin only)"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name=settings.aws_region)
        users_table = dynamodb.Table(settings.users_table)
        
        response = users_table.scan()
        users = response.get('Items', [])
        
        # Convert Decimal to float for JSON serialization
        def convert_decimals(obj):
            if isinstance(obj, list):
                return [convert_decimals(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: convert_decimals(value) for key, value in obj.items()}
            elif isinstance(obj, Decimal):
                return float(obj)
            return obj
        
        users = convert_decimals(users)
        
        # Format for frontend
        formatted_users = []
        for user in users:
            formatted_users.append({
                'id': user.get('userId', ''),
                'email': user.get('email', ''),
                'full_name': user.get('full_name', ''),
                'role': user.get('role', 'user'),
                'created_at': user.get('created_at', ''),
                'carbon_budget': user.get('carbon_budget', 500),
                'status': 'active'  # All users in DB are active for now
            })
        
        return {
            "users": formatted_users,
            "total": len(formatted_users)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )


@router.get("/pending-users")
async def get_pending_users(admin_user: Dict[str, Any] = Depends(require_admin)) -> Dict[str, Any]:
    """Get list of pending user registrations (admin only)"""
    # For now, return empty since our registration flow creates users directly
    # In future, could implement approval workflow
    return {
        "pending_users": [],
        "total": 0
    }


@router.get("/stats")
async def get_admin_stats(admin_user: Dict[str, Any] = Depends(require_admin)) -> Dict[str, Any]:
    """Get admin statistics (admin only)"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name=settings.aws_region)
        users_table = dynamodb.Table(settings.users_table)
        entries_table = dynamodb.Table(settings.entries_table)
        
        # Get user count
        users_response = users_table.scan(Select='COUNT')
        total_users = users_response.get('Count', 0)
        
        # Get entries count and total emissions
        entries_response = entries_table.scan()
        entries = entries_response.get('Items', [])
        total_entries = len(entries)
        
        # Calculate total emissions
        total_emissions = 0.0
        current_month = datetime.now().strftime("%Y-%m")
        monthly_entries = 0
        
        for entry in entries:
            # Convert Decimal to float
            co2_equiv = entry.get('co2_equivalent', 0)
            if isinstance(co2_equiv, Decimal):
                co2_equiv = float(co2_equiv)
            total_emissions += co2_equiv
            
            # Count current month entries
            entry_date = entry.get('date', '')
            if entry_date.startswith(current_month):
                monthly_entries += 1
        
        return {
            "total_users": total_users,
            "pending_registrations": 0,  # No pending system yet
            "active_this_month": monthly_entries,
            "total_carbon_tracked": round(total_emissions, 2),
            "total_entries": total_entries
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching admin stats: {str(e)}"
        )


@router.post("/users/{user_id}/approve")
async def approve_user(
    user_id: str, 
    admin_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """Approve a pending user (admin only)"""
    # Since we don't have pending users yet, just return success
    return {
        "message": "User approved successfully",
        "user_id": user_id
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str, 
    admin_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """Delete a user (admin only)"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name=settings.aws_region)
        users_table = dynamodb.Table(settings.users_table)
        entries_table = dynamodb.Table(settings.entries_table)
        
        # Don't allow deleting admin user
        if user_id == admin_user.get('user_id'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own admin account"
            )
        
        # Delete user from users table
        users_table.delete_item(Key={'userId': user_id})
        
        # Also delete user's emissions entries
        entries_response = entries_table.scan(
            FilterExpression="userId = :uid",
            ExpressionAttributeValues={':uid': user_id}
        )
        
        for entry in entries_response.get('Items', []):
            entries_table.delete_item(Key={
                'userId': user_id,
                'timestamp': entry['timestamp']
            })
        
        return {
            "message": "User deleted successfully",
            "user_id": user_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )